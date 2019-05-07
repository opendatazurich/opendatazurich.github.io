# Open Data Zurich API documentation

## Available APIs

1. [RIS-API (Ratshausinformationssystems), Gemeinderat Stadt Zürich (GRZ)](/ris-api/)


## Credits

This repository is based on this blogpost: https://peterevans.dev/posts/how-to-host-swagger-docs-with-github-pages/

---

# Development notes

The following notes help to setup a new API documentation project.

## Setup swagger

1. Download the latest stable release of the Swagger UI [here](https://github.com/swagger-api/swagger-ui/releases).

1. Extract the contents and copy the "dist" directory to the root of your repository.

1. Create a new directory for the API you want to describes
    ```
    mkdir -p my-api/docs
    ```

1. Move the file "index.html" from the directory "dist" to the new api directory.
    ```
    mv dist/index.html my-api/docs
    ```
    
1. Copy the YAML specification file for your API to the api directory.

1. Edit index.html and change the `url` property to reference your local YAML file. 
    ```javascript
        const ui = SwaggerUIBundle({
            url: "swagger.yaml",
        ...
    ```

1. Then fix any references to files in the "dist" directory.
    ```html
    ...
    <link rel="stylesheet" type="text/css" href="../../dist/swagger-ui.css" >
    <link rel="icon" type="image/png" href="../../dist/favicon-32x32.png" sizes="32x32" />
    <link rel="icon" type="image/png" href="../../dist/favicon-16x16.png" sizes="16x16" />    
    ...
    <script src="../../dist/swagger-ui-bundle.js"> </script>
    <script src="../../dist/swagger-ui-standalone-preset.js"> </script>    
    ...
    ```

1. Add a README.md in the api directory to describe the API
    ```
    touch my-api/README.md
    ```


## Installation of jupyter

```bash
# create a new virtualenv
virtualenv --no-site-packages pyenv
source ./pyenv/bin/activate

# install dependencies
pip install -r requirements.txt
```

Run the jupyter notebook:

```
./pyenv/bin/jupyter notebook
```

