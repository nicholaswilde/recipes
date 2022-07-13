# Development

## :smiley: Emoji

Emoji are manually added to the front of ingredients and cookware to give the pages a little bit of flare. My hopes is
that eventually this can be added to `cook-docs` as an automated task. For now, `emoji.yaml` can be used as reference.

```yaml title="emoji.yaml"
--8<-- "includes/emoji.yaml"
```

## :runner: Workflow

Below is my current workflow for documenting recipes.

``` mermaid
graph TD
  S[Change to or create ./cook/catetory dir];
  A{Does the source<br/>website exist?};
  B[Import recipe using cook-import];
  C[Manually write cook<br/>file using micro editor];
  D{Is the domain<br />supported by<br/>cook-import?};
  E[Visually check cook file];
  F[Test output using cook recipe read command];
  G[Download image file and rename<br/>to same base name as cook file];
  H[Run cook-docs in ./cook/category<br/>to generate markdown file];
  I[Manually check markdown file];
  J[Move markdown file to ./docs/category];
  K[Copy image to ./docs/assets/images<br/>with same base file name as markdown file];
  L[Add markdown file to mkdocs.yaml];
  M[Locally run mkdocs to test mkdocs-material];
  N[Commit and push to repo];
  O{Is the file<br />correct?};
  P[Edit cook file];
  Q{Is the<br/>output correct?};
  R[Edit cook file];
  T{Does the page<br/>render correctly?};
  U[CI GitHub Action workflow<br/>deploys recipe site];
  V{Is the image<br/>format webp?};
  W[Convert the image<br/>to png using dwebp];

  A --> |Yes|B;
  A --> |No|C;
  B --> D;
  C --> F;
  D --> |Yes|E;
  D --> |No|C;
  E --> F;
  F --> Q;
  Q --> |Yes|G;
  H --> I;
  J --> K;
  K --> L;
  L --> M;
  I --> O;
  O --> |Yes|J;
  O --> |No|P;
  P --> H;
  Q --> |No|R;
  R --> F;
  S --> A;
  M --> T;
  T --> |Yes|N;
  T --> |No|P
  N --> U;
  G --> V;
  V --> |Yes|W;
  V --> |No|H;
  W --> H

  click B "https://github.com/cooklang/cook-import"
  click C "https://github.com/nicholaswilde/cooklang-micro"
  click D "https://github.com/cooklang/cook-import"
  click F "https://cooklang.org/cli/help/#read"
  click H "https://nicholaswilde.io/cook-docs"
  click U "https://github.com/nicholaswilde/recipes/blob/main/.github/workflows/ci.yaml"
```

## :frame_with_picture: Convert webp to png

```shell title="Installation"
sudo apt install webp
```

```shell title="Convert"
dwebp file.webp -o file.png
```
