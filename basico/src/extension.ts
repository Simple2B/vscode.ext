// The module 'vscode' contains the VS Code extensibility API
// Import the module and reference it with the alias vscode in your code below
import * as vscode from 'vscode';
// import hover information
import * as hoverInfo from './hover_info.json';

// this method is called when your extension is activated
// your extension is activated the very first time the command is executed
export function activate(context: vscode.ExtensionContext) {
	// Use the console to output diagnostic information (console.log) and errors (console.error)
	// This line of code will only be executed once when your extension is activated
    console.log('Congratulations, your extension "BASICO" is now active!');

    // Register hover provider
    let disposable = vscode.languages.registerHoverProvider('basico', {

		/**
		 * Provide a hover for the given position and document. Multiple hovers at the same
		 * position will be merged by the editor. A hover can have a range which defaults
		 * to the word range at the position when omitted.
		 *
		 * @param document The document in which the command was invoked.
		 * @param position The position at which the command was invoked.
		 * @param token A cancellation token.
		 * @return A hover or a thenable that resolves to such. The lack of a result can be
		 * signaled by returning `undefined` or `null`.
		 */
		provideHover(document: vscode.TextDocument, position: vscode.Position, token: vscode.CancellationToken): vscode.ProviderResult<vscode.Hover> {
            const range = document.getWordRangeAtPosition(position);
            const word = document.getText(range);
            let hover = null;
            hoverInfo.forEach(element => {
                if (element.name == word) {
                    hover = new vscode.Hover({ language: 'basico', value: element.value.join('\n') });
                }
            });
            return hover;
        }
	});

    context.subscriptions.push(disposable);
}

// this method is called when your extension is deactivated
export function deactivate() {}
