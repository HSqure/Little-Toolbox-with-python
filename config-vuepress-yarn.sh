#!/bin/bash

corepack enable

git init
yarn init -2
yarn add -D vuepress@next


echo "nodeLinker: 'node-modules'" >> .yarnrc.yml

echo 'node_modules' >> .gitignore
echo '.temp' >> .gitignore
echo '.cache' >> .gitignore

mkdir -p docs

echo '请在其中中间加入：  

  ,
  "scripts": {
    "docs:dev": "vuepress dev docs",
    "docs:build": "vuepress build docs"
  } 
  
  
  '

gedit package.json

yarn install

mkdir docs
echo '# Hello VuePress aaagain!' > docs/README.md

yarn docs:dev
