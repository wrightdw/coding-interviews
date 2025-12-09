import { useEffect, useRef, useState } from 'react';
import { EditorView, keymap, lineNumbers, highlightActiveLineGutter, highlightSpecialChars, drawSelection, dropCursor, rectangularSelection, crosshairCursor, highlightActiveLine } from '@codemirror/view';
import { EditorState, Compartment } from '@codemirror/state';
import { defaultKeymap, history, historyKeymap } from '@codemirror/commands';
import { bracketMatching, indentOnInput, syntaxHighlighting, defaultHighlightStyle, foldGutter, foldKeymap } from '@codemirror/language';
import { closeBrackets, closeBracketsKeymap, completionKeymap } from '@codemirror/autocomplete';
import { searchKeymap, highlightSelectionMatches } from '@codemirror/search';
import { javascript } from '@codemirror/lang-javascript';
import { python } from '@codemirror/lang-python';
import { java } from '@codemirror/lang-java';
import { cpp } from '@codemirror/lang-cpp';
import { oneDark } from '@codemirror/theme-one-dark';
import { yCollab } from 'y-codemirror.next';
import * as Y from 'yjs';
import { WebrtcProvider } from 'y-webrtc';

const languageExtensions = {
  javascript: javascript(),
  python: python(),
  java: java(),
  cpp: cpp()
};

const languageTemplates = {
  javascript: '// Write your JavaScript code here\nfunction solution() {\n  \n}\n',
  python: '# Write your Python code here\ndef solution():\n    pass\n',
  java: '// Write your Java code here\npublic class Solution {\n    public static void main(String[] args) {\n        \n    }\n}\n',
  cpp: '// Write your C++ code here\n#include <iostream>\n\nint main() {\n    \n    return 0;\n}\n'
};

// Basic editor setup extensions
const basicSetup = [
  lineNumbers(),
  highlightActiveLineGutter(),
  highlightSpecialChars(),
  history(),
  foldGutter(),
  drawSelection(),
  dropCursor(),
  EditorState.allowMultipleSelections.of(true),
  indentOnInput(),
  syntaxHighlighting(defaultHighlightStyle, { fallback: true }),
  bracketMatching(),
  closeBrackets(),
  rectangularSelection(),
  crosshairCursor(),
  highlightActiveLine(),
  highlightSelectionMatches(),
  keymap.of([
    ...closeBracketsKeymap,
    ...defaultKeymap,
    ...searchKeymap,
    ...historyKeymap,
    ...foldKeymap,
    ...completionKeymap
  ])
];

function CollaborativeEditor({ sessionId, language, onCodeChange }) {
  const editorRef = useRef(null);
  const viewRef = useRef(null);
  const ydocRef = useRef(null);
  const providerRef = useRef(null);
  const languageCompartment = useRef(new Compartment());

  useEffect(() => {
    if (!editorRef.current) return;

    try {
      console.log('Initializing editor for session:', sessionId);

    // Create Yjs document
    const ydoc = new Y.Doc();
    ydocRef.current = ydoc;
    const ytext = ydoc.getText('codemirror');

    // Set up WebRTC provider for real-time collaboration
    const provider = new WebrtcProvider(`code-interview-${sessionId}`, ydoc, {
      signaling: ['wss://signaling.yjs.dev'],
    });
    providerRef.current = provider;

    // Initialize with template if empty
    if (ytext.length === 0) {
      ytext.insert(0, languageTemplates[language] || '');
    }

    // Create editor state
    const state = EditorState.create({
      doc: ytext.toString(),
      extensions: [
        ...basicSetup,
        languageCompartment.current.of(languageExtensions[language] || javascript()),
        oneDark,
        yCollab(ytext, provider.awareness),
        EditorView.updateListener.of((update) => {
          if (update.docChanged) {
            onCodeChange(update.state.doc.toString());
          }
        })
      ]
    });

    // Create editor view
    const view = new EditorView({
      state,
      parent: editorRef.current
    });
    viewRef.current = view;

    console.log('Editor initialized successfully');

    return () => {
      view.destroy();
      provider.destroy();
      ydoc.destroy();
    };
    } catch (error) {
      console.error('Error initializing editor:', error);
    }
  }, [sessionId]);

  // Update language when changed
  useEffect(() => {
    if (!viewRef.current) return;

    const view = viewRef.current;
    
    view.dispatch({
      effects: languageCompartment.current.reconfigure(languageExtensions[language] || javascript())
    });
  }, [language]);

  return <div ref={editorRef} className="editor-container" />;
}

export default CollaborativeEditor;
