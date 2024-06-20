import json
import os
import re
import shutil
import tempfile
import click
import git
from openapi_spec_validator import validate_spec

# Templates for various files
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

NODE_INDEX_TEMPLATE = """
import {{ INodeType, INodeTypeBaseDescription }} from 'n8n-workflow';
import {{ {name} }} from './nodes/{name}/{name}.node';

export const nodeTypes: INodeTypeBaseDescription[] = [
	{name},
];
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


def load_openapi_spec(file_path):
    with open(file_path, "r") as file:
        spec = json.load(file)
    validate_spec(spec)
    return spec


def create_node_properties(api_spec):
    properties = []
    for path, methods in api_spec["paths"].items():
        for method, details in methods.items():
            properties.append(
                f"""
            {{
                displayName: '{details.get('summary', method.upper() + " " + path)}',
                name: '{method}_{path.replace("/", "_").replace("{", "").replace("}", "")}',
                type: 'operation',
                default: '',
                options: []
            }}
            """
            )
    return ",".join(properties)


def load_dev_dependencies(starter_repo_path):
    with open(os.path.join(starter_repo_path, "package.json"), "r") as file:
        starter_package = json.load(file)
    return starter_package.get("devDependencies", {})


def clone_starter_repo(temp_dir):
    repo_url = "https://github.com/n8n-io/n8n-nodes-starter.git"
    git.Repo.clone_from(repo_url, temp_dir)


def create_plugin_files(api_spec, name, output_dir, temp_dir):
    node_properties = create_node_properties(api_spec)
    dev_dependencies = json.dumps(load_dev_dependencies(temp_dir), indent=4)

    # Copy n8n-nodes-starter template
    shutil.copytree(temp_dir, output_dir)

    # Write package.json
    with open(os.path.join(output_dir, "package.json"), "w") as file:
        file.write(
            PACKAGE_JSON_TEMPLATE.format(
                name=name.lower(), dev_dependencies=dev_dependencies
            )
        )

    # Write node index file
    with open(os.path.join(output_dir, "src", "index.ts"), "w") as file:
        file.write(NODE_INDEX_TEMPLATE.format(name=name))

    # Write node file
    node_dir = os.path.join(output_dir, "src", "nodes", name)
    os.makedirs(node_dir, exist_ok=True)
    with open(os.path.join(node_dir, f"{name}.node.ts"), "w") as file:
        file.write(NODE_TEMPLATE.format(name=name, properties=node_properties))

    # Write credentials file
    credentials_dir = os.path.join(output_dir, "src", "credentials")
    os.makedirs(credentials_dir, exist_ok=True)
    with open(os.path.join(credentials_dir, f"{name}Api.credentials.ts"), "w") as file:
        file.write(CREDENTIALS_TEMPLATE.format(name=name))


def validate_node_name(ctx, param, value):
    if not re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", value):
        raise click.BadParameter(
            "NODE_NAME should start with a letter or underscore and contain only letters, numbers, and underscores."
        )
    return value


@click.command()
@click.argument("openapi_file", type=click.Path(exists=True))
@click.argument("node_name", type=str, callback=validate_node_name)
@click.option(
    "--output_dir",
    type=click.Path(),
    default=None,
    help="Directory to save the generated plugin files. Defaults to ./{NODE_NAME}",
)
def generate_n8n_plugin(openapi_file, node_name, output_dir):
    """
    Generate n8n community node plugin from OpenAPI specification.

    OPENAPI_FILE: Path to the OpenAPI JSON file.
    NODE_NAME: Name of the n8n node.
    """
    if output_dir is None:
        output_dir = f"./{node_name}"

    with tempfile.TemporaryDirectory() as temp_dir:
        clone_starter_repo(temp_dir)
        api_spec = load_openapi_spec(openapi_file)
        create_plugin_files(api_spec, node_name, output_dir, temp_dir)
    click.echo(f"Generated n8n node plugin saved to {output_dir}")


if __name__ == "__main__":
    generate_n8n_plugin()
