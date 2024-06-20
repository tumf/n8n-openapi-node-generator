# n8n OpenAPI Node Plugin Generator

This project is a CLI tool that generates [n8n](https://n8n.io/) community node plugins from [OpenAPI specifications](https://swagger.io/specification/) . It simplifies the process of creating n8n nodes by automatically generating the necessary code based on your API's OpenAPI specification.

## Features

- Generate n8n node plugins from OpenAPI JSON files
- Create TypeScript files for nodes and credentials
- Automatically build the required project structure


## Supported OpenAPI Versions

This generator supports OpenAPI 3.0.x.


## Installation

First, clone the repository:

```bash
git clone https://github.com/tumf/n8n-openapi-node-plugin-generator.git
cd n8n-openapi-node-plugin-generator
```

Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Usage

To generate an n8n node plugin, use the following command:

```bash
python generate_n8n_plugin.py path/to/openapi.json path/to/output/dir NodeName
```

### Arguments

- `openapi_file`: Path to the OpenAPI JSON file.
- `output_dir`: Directory to save the generated plugin files.
- `node_name`: Name of the n8n node.

### Example

```bash
python generate_n8n_plugin.py openapi.json ./my-n8n-plugin MyApi
```

This command will generate a new n8n node plugin for the API defined in `openapi.json` and save the generated files to `./my-n8n-plugin`.

## Project Structure

The generated plugin will have the following structure:

```
plugin/
├── src/
│   ├── nodes/
│   │   └── MyApi/
│   │       └── MyApi.node.ts
│   ├── MyApi.node.ts
│   └── MyApi.credentials.ts
├── package.json
└── tsconfig.json
```

- `src/nodes/MyApi/MyApi.node.ts`: The main node implementation file.
- `src/MyApi.credentials.ts`: The credentials file for the API.
- `package.json`: The package configuration file.
- `tsconfig.json`: The TypeScript configuration file.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request or open an issue.

## License

This project is licensed under the MIT License.
