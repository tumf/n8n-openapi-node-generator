# templates.py

PACKAGE_JSON_TEMPLATE = """
{{
  "name": "n8n-nodes-{name}",
  "version": "0.1.0",
  "description": "n8n nodes for {name} API",
  "keywords": [
    "n8n-community-node-package",
    "n8n-openapi-node-plugin-generator"
  ],
  "license": "MIT",
  "homepage": "",
  "author": {{
    "name": "",
    "email": ""
  }},
  "repository": {{
    "type": "git",
    "url": "https://github.com/<...>/n8n-nodes-<...>.git"
  }},
  "main": "index.js",
  "scripts": {{
    "build": "tsc && gulp build:icons",
    "dev": "tsc --watch",
    "format": "prettier nodes credentials --write",
    "lint": "eslint nodes credentials package.json",
    "lintfix": "eslint nodes credentials package.json --fix",
    "prepublishOnly": "npm run build && npm run lint -c .eslintrc.prepublish.js nodes credentials package.json"
  }},
  "files": [
    "dist"
  ],
  "n8n": {{
    "n8nNodesApiVersion": 1,
    "credentials": [
      "dist/credentials/{name}.credentials.js"
    ],
    "nodes": [
      "dist/nodes/{name}/{name}.node.js"
    ]
  }},
  "devDependencies": {dev_dependencies},
  "peerDependencies": {{
    "n8n-workflow": "*"
  }}
}}
"""

NODE_TEMPLATE = """
import {{ IExecuteFunctions }} from 'n8n-core';
import {{ INodeExecutionData, INodeType, INodeTypeDescription }} from 'n8n-workflow';

export class {name} implements INodeType {{
	description: INodeTypeDescription = {{
		displayName: '{name}',
		name: '{name}',
		icon: 'file:{name}.svg',
		group: ['transform'],
		version: 1,
		description: 'Consume {name} API',
		defaults: {{
			name: '{name}',
		}},
		inputs: ['main'],
		outputs: ['main'],
		properties: [
			{properties}
		],
	}};

	async execute(this: IExecuteFunctions): Promise<INodeExecutionData[][]> {{
		// Implementation of the node's execution
		return [[]];
	}}
}}
"""

CREDENTIALS_TEMPLATE = """
import {{ ICredentialType, INodeProperties }} from 'n8n-workflow';

export class {name}Api implements ICredentialType {{
	name = '{name}Api';
	displayName = '{name} API';
	properties: INodeProperties[] = [
		{{
			displayName: 'API Key',
			name: 'apiKey',
			type: 'string',
			default: '',
		}},
	];
}}
"""
