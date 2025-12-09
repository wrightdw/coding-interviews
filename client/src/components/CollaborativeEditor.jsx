import { useEffect, useRef } from 'react';
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

function CollaborativeEditor({ sessionId, language, onCodeChange, initialCode = '' }) {
  const editorRef = useRef(null);
  const viewRef = useRef(null);
  const languageCompartment = useRef(new Compartment());
  const isUpdatingFromProp = useRef(false);

  useEffect(() => {
    if (!editorRef.current) return;

    try {
      console.log('Initializing editor for session:', sessionId);

      // Get initial content
      const initialContent = initialCode || languageTemplates[language] || '';

      // Create editor state
      const state = EditorState.create({
        doc: initialContent,
        extensions: [
          ...basicSetup,
          languageCompartment.current.of(languageExtensions[language] || javascript()),
          oneDark,
          EditorView.updateListener.of((update) => {
            if (update.docChanged && !isUpdatingFromProp.current) {
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

  // Update content when initialCode prop changes (from WebSocket)
  useEffect(() => {
    if (!viewRef.current || !initialCode) return;

    const view = viewRef.current;
    const currentContent = view.state.doc.toString();

    // Only update if content is different
    if (currentContent !== initialCode) {
      isUpdatingFromProp.current = true;
      
      view.dispatch({
        changes: {
          from: 0,
          to: currentContent.length,
          insert: initialCode
        }
      });

      isUpdatingFromProp.current = false;
    }
  }, [initialCode]);

  return <div ref={editorRef} className="editor-container" />;
}

export default CollaborativeEditor;
