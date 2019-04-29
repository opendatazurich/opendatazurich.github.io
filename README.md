# Open Data Zurich API documentation

## Available APIs

1. [RIS-API](/ris-api/)

## Installation

This repository is based on this blogpost: https://peterevans.dev/posts/how-to-host-swagger-docs-with-github-pages/

### Steps

1. Download the latest stable release of the Swagger UI [here](https://github.com/swagger-api/swagger-ui/releases).

2. Extract the contents and copy the "dist" directory to the root of your repository.

3. Create a new directory for the API you want to describes
    ```
    mkdir my-api
    ```

4. Move the file "index.html" from the directory "dist" to the new api directory.
    ```
    mv dist/index.html my-api
    ```
    
5. Copy the YAML specification file for your API to the api directory.

6. Edit index.html and change the `url` property to reference your local YAML file. 
6. Edit index.html and change the `url` property to reference your local YAML file. 
    ```javascript
        const ui = SwaggerUIBundle({
            url: "swagger.yaml",
        ...
    ```
    Then fix any references to files in the "dist" directory.
    ```html
    ...
    <link rel="stylesheet" type="text/css" href="../dist/swagger-ui.css" >
    <link rel="icon" type="image/png" href="../dist/favicon-32x32.png" sizes="32x32" />
    <link rel="icon" type="image/png" href="../dist/favicon-16x16.png" sizes="16x16" />    
    ...
    <script src="../dist/swagger-ui-bundle.js"> </script>
    <script src="../dist/swagger-ui-standalone-preset.js"> </script>    
    ...
    ```