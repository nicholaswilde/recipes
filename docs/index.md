# :green_salad: Recipes :book:

My collection of recipes made with [cooklang][1]. 

The `cooklang` files are stored in the `cook` folder and the markdown files are stored
in the `docs` folder.

## :runner: Workflow

1. Determine the category of the recipe.
2. Change dir to the `./cook/<category>` or make dir.
3. Use [`cook-import`][2] to download the recipe from a website if possible.
4. Edit the `*.cook` file manually and compare to website.
5. Download the image file.
6. Convert from webp to png if required.
7. Run [`cook-docs`][3] to create markdown.
8. Edit the `*.md` file and add emoji if needed.
9. Copy the image to the `./docs/assets/images` directory.
10. Copy the `*.md` markdown file to the `./docs/<category>/` directory. Make dir if needed.
11. Add the new recipe to the `nav` section in `mkdocs.yml`.
12. Push the changes to the repo where GitHub action will update `mkdocs`.

### :frame_with_picture: Convert webp to png

```shell title="Installation"
sudo apt install webp
```

```shell title="Convert"
dwebp file.webp -o file.png
```

## ​:scales:​License

​[Apache 2.0 License](./LICENSE) 

## ​:pencil:​Author

​This project was started in 2022 by [​Nicholas Wilde​][4].

[1]: https://cooklang.org/
[2]: https://github.com/cooklang/cook-import
[3]: https://nicholaswilde.io/cook-docs
[4]: https://github.com/nicholaswilde/
