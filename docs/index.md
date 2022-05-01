# :green_salad: Recipes :book:

My collection of recipes made with [cooklang][1]. Currently, I download the
recipes using `cooklang` and then manually export and create the markdown
files for `mkdocs`. Hopefully, at some point, I can make a go template
converter to automatically generate the markdown files.

The `cooklang` files are stored in the `cook` folder and the markdown files are stored
in the `docs` folder.

## :runner: Workflow

1. Determine the category of the food.
2. Change dir to the `./cook/<category>` or make dir.
3. Use `cook-import` to download the recipe from a website if possible.
4. Edit the `*.cook` file manually and compare to website.
5. Download the image file.
6. Convert from webp to png if required.
7. Run `cook-docs`.
8. Edit the `*.md` file and add emoji if needed.
9. Copy the image to the `./docs/assets/imgaes` folder.
10. Copy the `*.md` file to the `./docs/<category>/` folder. Make dir if needed.
11. Add the new recipe to the `nav` section in `mkdocs.yml`.
12. Push the changes where GitHub action will update mkdocs.

### :frame_with_picture: Convert webp to png

```shell title="Installation"
sudo apt install webp
```

```shell title="Convert"
dwebp file.webp -o file.png
```

## ​:scales:​&nbsp;​ License

​[​Apache 2.0 License​](./LICENSE) 

## ​:pencil:​&nbsp;​ Author

​This project was started in 2022 by [​Nicholas Wilde​](https://github.com/nicholaswilde/).

[1]: https://cooklang.org/
