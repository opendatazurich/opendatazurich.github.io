# How to host Swagger API documentation with GitHub Pages
[<img alt="The blog of Peter Evans: How to Host Swagger Documentation With Github Pages" title="View blog post" src="https://peterevans.dev/img/blog-published-badge.svg">](https://peterevans.dev/posts/how-to-host-swagger-docs-with-github-pages/)

This describes how use the [Swagger UI](https://github.com/swagger-api/swagger-ui) to dynamically generate beautiful documentation for your API and host it for free with GitHub Pages.

The example API specification used by this repository can be seen hosted at [https://peter-evans.github.io/swagger-github-pages](https://peter-evans.github.io/swagger-github-pages/).

## Steps

1. Download the latest stable release of the Swagger UI [here](https://github.com/swagger-api/swagger-ui/releases).

2. Extract the contents and copy the "dist" directory to the root of your repository.

3. Create a new directory for the API you want to describes
    ```
    mkdir my-api
    ```

3. Move the file "index.html" from the directory "dist" to the new api directory.
    ```
    mv dist/index.html my-api
    ```
    
4. Copy the YAML specification file for your API to the api directory.

5. Edit [index.html](index.html) and change the `url` property to reference your local YAML file. 
    ```javascript
        const ui = SwaggerUIBundle({
            url: "swagger.yaml",
        ...
    ```
    Then fix any references to files in the "dist" directory.
    ```html
    ...
    <link rel="stylesheet" type="text/css" href="dist/swagger-ui.css" >
    <link rel="icon" type="image/png" href="dist/favicon-32x32.png" sizes="32x32" />
    <link rel="icon" type="image/png" href="dist/favicon-16x16.png" sizes="16x16" />    
    ...
    <script src="dist/swagger-ui-bundle.js"> </script>
    <script src="dist/swagger-ui-standalone-preset.js"> </script>    
    ...
    ```