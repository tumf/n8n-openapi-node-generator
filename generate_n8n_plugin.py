import json
import os
import shutil
import click
from openapi_spec_validator import validate_spec

# Templates for various files
PACKAGE_JSON_TEMPLATE = """
{
  "name": "n8n-nodes-{name}",
  "version": "0.1.0",
  "description": "n8n nodes for {name} API",
  "main": "./dist/index.js",
  "scripts": {
    "build": "tsc && tsc-alias",
    "dev": "tsc --watch"
  },
  "author": "",
  "license": "MIT",
  "devDependencies": {
    "@types/node": "^14.0.23",
    "tsc-alias": "^1.3.7",
    "typescript": "^4.1.2"
  }
}
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


def create_plugin_files(api_spec, name, output_dir):
    node_properties = create_node_properties(api_spec)

    # Copy n8n-nodes-starter template
    shutil.copytree("n8n-nodes-starter", output_dir)

    # Write package.json
    with open(os.path.join(output_dir, "package.json"), "w") as file:
        file.write(PACKAGE_JSON_TEMPLATE.format(name=name.lower()))

    # Write node index file
    with open(os.path.join(output_dir, "src", "index.ts"), "w") as file:
        file.write(NODE_INDEX_TEMPLATE.format(name=name))

    # Write node file
    node_dir = os.path.join(output_dir, "src", "nodes", name)
    os.makedirs(node_dir, exist_ok=True)
    with open(os.path.join(node_dir, f"{name}.node.ts"), "w") as file:
        file.write(NODE_TEMPLATE.format(name=name, properties=node_properties))

    # Write credentials file
    with open(
        os.path.join(output_dir, "src", "credentials", f"{name}Api.credentials.ts"), "w"
    ) as file:
        file.write(CREDENTIALS_TEMPLATE.format(name=name))


@click.command()
@click.argument("openapi_file", type=click.Path(exists=True))
@click.argument("output_dir", type=click.Path())
@click.argument("node_name", type=str)
def generate_n8n_plugin(openapi_file, output_dir, node_name):
    """
    Generate n8n community node plugin from OpenAPI specification.

    OPENAPI_FILE: Path to the OpenAPI JSON file.
    OUTPUT_DIR: Directory to save the generated plugin files.
    NODE_NAME: Name of the n8n node.
    """
    api_spec = load_openapi_spec(openapi_file)
    create_plugin_files(api_spec, node_name, output_dir)
    click.echo(f"Generated n8n node plugin saved to {output_dir}")


if __name__ == "__main__":
    generate_n8n_plugin()
