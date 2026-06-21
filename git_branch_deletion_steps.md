want to change branch pointing from master to main and to delete master branch 
```bash
$ git branch -a
* main
  remotes/origin/HEAD -> origin/master
  remotes/origin/dev1
  remotes/origin/main
  remotes/origin/master
  remotes/origin/uat1
```bash

changed  default branch in GitHub in github web 

GitHub repo → Settings → Branches → Default branch → change master to main

```bash
$ git log --oneline --all --graph --decorate
* 307687e (HEAD -> main, origin/main) updated comments
* 6dd0252 troubleshooting  files updated
* 2057739 uploaded to git
* 06c9c01 (origin/master, origin/HEAD) Delete myfile
* 2a8f6ee Delete m1
* e06d6e7 gitlab
* 2aff1ca (origin/uat1, origin/dev1) m1
* 0c87d55 07decfile
```

```bash
shekk@Shekkar MINGW64 /d/kind-k8s-troubleshooting-lab (main)
$ git remote set-head origin main
```bash

modified to main one 
```bash
shekk@Shekkar MINGW64 /d/kind-k8s-troubleshooting-lab (main)
$ git branch -a
* main
  remotes/origin/HEAD -> origin/main
  remotes/origin/dev1
  remotes/origin/main
  remotes/origin/master
  remotes/origin/uat1
```

deleted master mapped to main also deleted other branches from web after sync shows only branch 

 ```bash
  $ git push origin --delete master
To https://github.com/shekar1221/kind-k8s-troubleshooting-lab.git
 - [deleted]         master

shekk@Shekkar MINGW64 /d/kind-k8s-troubleshooting-lab (main)
$ git fetch --prune
From https://github.com/shekar1221/kind-k8s-troubleshooting-lab
 - [deleted]         (none)     -> origin/dev1
 - [deleted]         (none)     -> origin/uat1

shekk@Shekkar MINGW64 /d/kind-k8s-troubleshooting-lab (main)
$ git branch -a
* main
  remotes/origin/HEAD -> origin/main
  remotes/origin/main

shekk@Shekkar MINGW64 /d/kind-k8s-troubleshooting-lab (main)
$ git checkout main
Already on 'main'
Your branch is up to date with 'origin/main'.

shekk@Shekkar MINGW64 /d/kind-k8s-troubleshooting-lab (main)
$

  
```
