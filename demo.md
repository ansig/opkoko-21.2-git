# Demos

## Objects

### Blobs

För att spara en fil direkt i Git kan vi använa kommandod `hash-object`:

```bash
$ echo "version 1" > file1.txt
$ git hash-object -w file1.txt
83baae61804e65cc73a7201a7252750c76066a30
$ tree .git/objects/
.git/objects/
├── 83
│   └── baae61804e65cc73a7201a7252750c76066a30
├── info
└── pack
```

Vi ser att objektet sparats i en komprimerad fil och att dess innehåll är text-strängen "version 1":

```bash
$ file .git/objects/83/baae61804e65cc73a7201a7252750c76066a30
.git/objects/83/baae61804e65cc73a7201a7252750c76066a30: zlib compressed data
$ git cat-file -t 83baae61804e65cc73a7201a7252750c76066a30
blob
$ git cat-file -p 83baae61804e65cc73a7201a7252750c76066a30
version 1
```

Om vi ändrar innehållet i den första filen och skapar en ny fil med ett annat innehåll så får vi fler blobs i databasen:

```bash
$ echo "version 2" > file1.txt
$ git hash-object -w file1.txt
1f7a7a472abf3dd9643fd615f6da379c4acb3e3a
$ echo "foo" > file2.txt
$ git hash-object -w file2.txt
257cc5642cb1a054f08cc83f2d943e56fd3ebe99
$ tree .git/objects/
.git/objects/
├── 1f
│   └── 7a7a472abf3dd9643fd615f6da379c4acb3e3a
├── 25
│   └── 7cc5642cb1a054f08cc83f2d943e56fd3ebe99
├── 83
│   └── baae61804e65cc73a7201a7252750c76066a30
├── info
└── pack

5 directories, 3 files
```

Notera att vi alltså nu har 3 stycken separata objekt, trots att vi bara har 2 filer. Det är för att varje blob representerar innehållet i en fil och att varje version av detta innehåll sparas i sin helhet i databasen.

När Git jobbar med olika versioner av filer så läser den helt enkelt ut innehållet i en specifik blob till en fil i arbetsytan. T ex, om vi vill återställa den första versionen av `file1.txt`:

```bash
$ cat file1.txt
version 2
$ git cat-file -p 83baae61804e65cc73a7201a7252750c76066a30 > file1.txt
$ cat file1.txt
version 1
```

Vi har nu heller ingen aning om namn eller plats i filstrukturen. För detta använder Git en annan typ av objekt: träd.

### Trees

Ett träd (tree) i Git representerar en katalogstruktur. Varje objekt innehåller en lista över blobs och/eller andra träd-objekt, ungeär som directory entries och inodes i ett filsystem.

Det är träden som representerar en ögonblicksbild av arbetskatalogen, dvs vilka filer som inns och deras innehåll.

För att t ex skapa ett träd som representerar första versionen av vårt projekt så gör vi följande träd:

```bash
$ printf "100644 blob 83baae61804e65cc73a7201a7252750c76066a30\tfile1.txt" | git mktree
b7e8fac7e3e35d93d39d2fa2260868f025a9efb4
$ tree .git/objects/
.git/objects/
├── 1f
│   └── 7a7a472abf3dd9643fd615f6da379c4acb3e3a
├── 25
│   └── 7cc5642cb1a054f08cc83f2d943e56fd3ebe99
├── 83
│   └── baae61804e65cc73a7201a7252750c76066a30
├── b7
│   └── e8fac7e3e35d93d39d2fa2260868f025a9efb4
├── info
└── pack

6 directories, 4 files
$ git cat-file -t b7e8fac7e3e35d93d39d2fa2260868f025a9efb4
tree
$ git cat-file -p b7e8fac7e3e35d93d39d2fa2260868f025a9efb4
100644 blob 83baae61804e65cc73a7201a7252750c76066a30	file1.txt
```

Den andra versionen av vårt projekt kan vi representera med ett träd-objekt med 2 rader:

```bash
$ printf "100644 blob 1f7a7a472abf3dd9643fd615f6da379c4acb3e3a\tfile1.txt" > /tmp/tree.txt
$ printf "\n100644 blob 257cc5642cb1a054f08cc83f2d943e56fd3ebe99\tfile2.txt" >> /tmp/tree.txt
$ cat /tmp/tree.txt && echo
100644 blob 1f7a7a472abf3dd9643fd615f6da379c4acb3e3a	file1.txt
100644 blob 257cc5642cb1a054f08cc83f2d943e56fd3ebe99	file2.txt
$ cat /tmp/tree.txt | git mktree
b5556083f4a97bb5d46905fb2b900c05259ff250
$ git cat-file -p b5556083f4a97bb5d46905fb2b900c05259ff250
100644 blob 1f7a7a472abf3dd9643fd615f6da379c4acb3e3a	file1.txt
100644 blob 257cc5642cb1a054f08cc83f2d943e56fd3ebe99	file2.txt
$ tree .git/objects/
.git/objects/
├── 07
│   └── c4045f144b11f28f110bd1f747e4e04c028b9b
├── 1f
│   └── 7a7a472abf3dd9643fd615f6da379c4acb3e3a
├── 25
│   └── 7cc5642cb1a054f08cc83f2d943e56fd3ebe99
├── 83
│   └── baae61804e65cc73a7201a7252750c76066a30
├── b5
│   └── 556083f4a97bb5d46905fb2b900c05259ff250
├── b7
│   └── e8fac7e3e35d93d39d2fa2260868f025a9efb4
├── info
└── pack

8 directories, 6 files
```

Låt oss också göra en tredje version där vi lägger till ytterligare en fil i en underkatalog. Då behöver vi först skapa ett träd för underkatalogen och sedan ett träd som refererar både till våra beffintliga filer och till underkatalogen:

```bash
$ printf "100644 blob 83baae61804e65cc73a7201a7252750c76066a30\tfile3.txt" | git mktree # NOTERA: kom ihåg att sha-summan för innehållet är samma som "version 1"
c551f28adbcdd0da8892240b632c3613eee6a50c
$ cat /tmp/tree.txt && echo
100644 blob 1f7a7a472abf3dd9643fd615f6da379c4acb3e3a	file1.txt
100644 blob 257cc5642cb1a054f08cc83f2d943e56fd3ebe99	file2.txt
$ printf "\n040000 tree c551f28adbcdd0da8892240b632c3613eee6a50c\tdir1" >> /tmp/tree.txt
$ cat /tmp/tree.txt && echo
100644 blob 1f7a7a472abf3dd9643fd615f6da379c4acb3e3a	file1.txt
100644 blob 257cc5642cb1a054f08cc83f2d943e56fd3ebe99	file2.txt
040000 tree c551f28adbcdd0da8892240b632c3613eee6a50c	dir1
$ cat /tmp/tree.txt | git mktree
2922bfc1b7c3765f0e06966b731af191110127a4
$ git cat-file -p 2922bfc1b7c3765f0e06966b731af191110127a4
040000 tree c551f28adbcdd0da8892240b632c3613eee6a50c	dir1
100644 blob 1f7a7a472abf3dd9643fd615f6da379c4acb3e3a	file1.txt
100644 blob 257cc5642cb1a054f08cc83f2d943e56fd3ebe99	file2.txt
$ tree .git/objects/
.git/objects/
├── 1f
│   └── 7a7a472abf3dd9643fd615f6da379c4acb3e3a
├── 25
│   └── 7cc5642cb1a054f08cc83f2d943e56fd3ebe99
├── 29
│   └── 22bfc1b7c3765f0e06966b731af191110127a4
├── 83
│   └── baae61804e65cc73a7201a7252750c76066a30
├── b5
│   └── 556083f4a97bb5d46905fb2b900c05259ff250
├── b7
│   └── e8fac7e3e35d93d39d2fa2260868f025a9efb4
├── c5
│   └── 51f28adbcdd0da8892240b632c3613eee6a50c
├── info
└── pack

9 directories, 7 files
```

## Commits

Låt oss skapa en commit:

```bash
$ echo "First commit" | git commit-tree b7e8fac7e3e35d93d39d2fa2260868f025a9efb4
<COMMIT 1 SHA>
$ git cat-file -t <COMMIT 1 SHA>
commit
$ git cat-file -p <COMMIT 1 SHA>
tree b7e8fac7e3e35d93d39d2fa2260868f025a9efb4
author Anders Sigfridsson <anders.sigfridsson@omegapoint.se> 1649361615 +0200
committer Anders Sigfridsson <anders.sigfridsson@omegapoint.se> 1649361615 +0200

First commit
```

Det här objektet innehåller alltså information om vem som skapade en viss version av vårt projekt och när detta skedde.

Låt oss även skapa commits för våra andra träd:

```bash
$ echo "Second commit" | git commit-tree -p <c> b5556083f4a97bb5d46905fb2b900c05259ff250
<COMMIT 2 SHA>
$ echo "Third commit" | git commit-tree -p <COMMIT 2 SHA> 2922bfc1b7c3765f0e06966b731af191110127a4
<COMMIT 3 SHA>
$ git cat-file -p <COMMIT 3 SHA>
tree 2922bfc1b7c3765f0e06966b731af191110127a4
parent afaa7f6737fc7b63d4dbc4c0b7ec2661472ce50b
author Anders Sigfridsson <anders.sigfridsson@omegapoint.se> 1649398967 +0200
committer Anders Sigfridsson <anders.sigfridsson@omegapoint.se> 1649398967 +0200

Third commit
```

Eftersom varje commit kan referera till en förälder har vi nu en historik:

```bash
$ git log --oneline SHA3
SHA3 Third commit
SHA2 Second commit
SHA1 First commit
```

## References

```bash
$ git log
fatal: your current branch 'main' does not have any commits yet
$ git log --oneline SHA3
...
$ echo "<COMMIT 3 SHA>" > .git/refs/heads/main
$ git log
SHA3 Third commit
SHA2 Second commit
SHA1 First commit
$ echo "<COMMIT 2 SHA>" > .git/res/heads/other
$ git log other
...
```

## Index

För denna demo skapar vi ett nytt repo och gör en initial commit:

```bash
$ mkdir index-demo && cd index-demo
$ git init
$ echo "file1 v1" > file1
$ echo "file2 v1" > file2
$ git add file* && git commit -m 'Initial commit'
$ find .git/objects/ -type f
.git/objects//09/c717ae68b68fa9cb45beb256e7f2b220d6a05c
.git/objects//af/7a6ca531e75993bad5153085d27137ba618f11
.git/objects//b9/32a3680a096754826129aee308c64e31c27a29
.git/objects//83/41d3ed4a2b75dd440efd4c794e8c4a8ea70654
```

Vi ser att vi har 4 objekt nu: 1 commit, 1 träd och 2 blobs.

Vi kan också se att det vi just nu har i vårt index är samma träd:

```bash
$ git ls-files -s
100644 09c717ae68b68fa9cb45beb256e7f2b220d6a05c 0	file1
100644 af7a6ca531e75993bad5153085d27137ba618f11 0	file2
```

Om vi då gör en ändring i `file2` får vi ett smutsigt index, dvs vårt index stämmer inte med filerna i arbetsytan:

```bash
$ echo "file2 v2" > file2
$ git status
On branch main
Changes not staged for commit:
  (use "git add <file>..." to update what will be committed)
  (use "git restore <file>..." to discard changes in working directory)
	modified:   file2

no changes added to commit (use "git add" and/or "git commit -a")
$ git ls-files -s
100644 09c717ae68b68fa9cb45beb256e7f2b220d6a05c 0	file1
100644 af7a6ca531e75993bad5153085d27137ba618f11 0	file2
```

Om vi då lägger till den ändrade filen så har vi fortfarande ett smutsigt index. Nu finns ett nytt objekt i databasen, men trädet i vårt index stämmer inte med det träd som ligger i databasen:

```bash
$ git add file2
$ git status
On branch main
Changes to be committed:
  (use "git restore --staged <file>..." to unstage)
	modified:   file2

$ find .git/objects/ -type f
.git/objects//1a/7cbf33f6bf0b9ec0f116aa6a6328e830e71607
.git/objects//09/c717ae68b68fa9cb45beb256e7f2b220d6a05c
.git/objects//af/7a6ca531e75993bad5153085d27137ba618f11
.git/objects//b9/32a3680a096754826129aee308c64e31c27a29
.git/objects//83/41d3ed4a2b75dd440efd4c794e8c4a8ea70654
$ git ls-files -s # detta är trädet i index
100644 09c717ae68b68fa9cb45beb256e7f2b220d6a05c 0	file1
100644 1a7cbf33f6bf0b9ec0f116aa6a6328e830e71607 0	file2
$ git cat-file -p b932a3680a096754826129aee308c64e31c27a29 # detta är trädet vi sen tidigare sparat i databasen
100644 blob 09c717ae68b68fa9cb45beb256e7f2b220d6a05c	file1
100644 blob af7a6ca531e75993bad5153085d27137ba618f11	file2
```

När vi till slut gör en förbindelse så skapas 2 nya objekt i databasen, en commit och ett träd. Vi har inte längre ett smutsigt index:

```bash
$ git commit -m 'Change file2'
[main a111479] Change file2
 1 file changed, 1 insertion(+), 1 deletion(-)
$ find .git/objects/ -type f
.git/objects//32/8e630d2afd6ed6dd48e155cbecc9a4bd1cf86b
.git/objects//1a/7cbf33f6bf0b9ec0f116aa6a6328e830e71607
.git/objects//09/c717ae68b68fa9cb45beb256e7f2b220d6a05c
.git/objects//af/7a6ca531e75993bad5153085d27137ba618f11
.git/objects//b9/32a3680a096754826129aee308c64e31c27a29
.git/objects//a1/1147927c430c9a4169ed357a614bc1ee39e26b
.git/objects//83/41d3ed4a2b75dd440efd4c794e8c4a8ea70654
$ git cat-file -p 328e630d2afd6ed6dd48e155cbecc9a4bd1cf86b # det här är det nya träd-objektet
100644 blob 09c717ae68b68fa9cb45beb256e7f2b220d6a05c	file1
100644 blob 1a7cbf33f6bf0b9ec0f116aa6a6328e830e71607	file2
$ git ls-files -s # det här är vårt nuvarande index
100644 09c717ae68b68fa9cb45beb256e7f2b220d6a05c 0	file1
100644 1a7cbf33f6bf0b9ec0f116aa6a6328e830e71607 0	file2
$ git status
On branch main
nothing to commit, working tree clean
```

## Pack-files

Vi börjar med att lägga till en lite större fil till vårt repo:

```bash
$ cp -r refs-demo/ pack-demo
$ cd pack-demo
$ git reset --hard main
$ curl -O https://raw.githubusercontent.com/ansible/ansible/devel/lib/ansible/modules/file.py
$ du -sh *
4.0K	dir1
 40K	file.py
4.0K	file1.txt
4.0K	file2.txt
$ git add file.py && git commit -m 'Add file.py'
$ git cat-file -p main^{tree}
040000 tree c551f28adbcdd0da8892240b632c3613eee6a50c	dir1
100644 blob 34f9249087d91558a478c498a4def7e0aaea72c5	file.py
100644 blob 1f7a7a472abf3dd9643fd615f6da379c4acb3e3a	file1.txt
100644 blob 257cc5642cb1a054f08cc83f2d943e56fd3ebe99	file2.txt
$ git cat-file -s 34f9249087d91558a478c498a4def7e0aaea72c5
39997
$ du -sh .git/objects/34/f9249087d91558a478c498a4def7e0aaea72c5
 12K	.git/objects/34/f9249087d91558a478c498a4def7e0aaea72c5
```

Så vad händer om vi nu modifierar den här filen lite?

```bash
$ echo "# Just testing" >> file.py
$ git add file.py && git commit -m 'Modify file.py'
[main eae5fa9] Modify file.py
 1 file changed, 1 insertion(+)
$ git cat-file -p main^{tree}
040000 tree c551f28adbcdd0da8892240b632c3613eee6a50c	dir1
100644 blob 4419a8c1f4dd35bb47fbd79e68b8c439df54b4ef	file.py
100644 blob 1f7a7a472abf3dd9643fd615f6da379c4acb3e3a	file1.txt
100644 blob 257cc5642cb1a054f08cc83f2d943e56fd3ebe99	file2.txt
$ git cat-file -s 4419a8c1f4dd35bb47fbd79e68b8c439df54b4ef
40012
$ du -sh .git/objects/*
4.0K	.git/objects/1f
4.0K	.git/objects/25
4.0K	.git/objects/29
4.0K	.git/objects/2f
 12K	.git/objects/34
 12K	.git/objects/44
4.0K	.git/objects/59
4.0K	.git/objects/66
4.0K	.git/objects/83
4.0K	.git/objects/86
4.0K	.git/objects/8c
4.0K	.git/objects/b5
4.0K	.git/objects/b7
4.0K	.git/objects/c5
4.0K	.git/objects/e4
4.0K	.git/objects/ea
4.0K	.git/objects/eb
```

Men för att åtgärda detta kan vi köra `git gc`:

```bash
$ git gc
Enumerating objects: 16, done.
Counting objects: 100% (16/16), done.
Delta compression using up to 4 threads
Compressing objects: 100% (11/11), done.
Writing objects: 100% (16/16), done.
Total 16 (delta 3), reused 0 (delta 0), pack-reused 0
$ du -sh .git/objects/*
4.0K	.git/objects/e4
8.0K	.git/objects/info
 16K	.git/objects/pack
```

Fråga: vad är det för objekt som ligger kvar efter att vi har gjort `git gc` och fått en pack-fil?
Svar: det är de objekt vi skapat som inte pekas av någon commit!

```
$ git verify-pack -v .git/objects/pack/pack-97bcb4e19ee5a14805411adee73372abfd76a0b0.idx
eae5fa998beaf604a5756fd04da2df65522c3604 commit 269 169 12
eb14a8fc39a80dac8277cbb2cb76573abd135fdd commit 266 165 181
869a278f4a4a7ae04c95086ccb69af1e07fa2904 commit 267 161 346
6637401b91b0f98c1e9acb7ded97daee8009136c commit 268 162 507
2f2e8c2796babefd027da63ab6cd979b5f812190 commit 89 98 669 1 eb14a8fc39a80dac8277cbb2cb76573abd135fdd
83baae61804e65cc73a7201a7252750c76066a30 blob   10 19 767
4419a8c1f4dd35bb47fbd79e68b8c439df54b4ef blob   40012 8945 786
1f7a7a472abf3dd9643fd615f6da379c4acb3e3a blob   10 19 9731
257cc5642cb1a054f08cc83f2d943e56fd3ebe99 blob   4 13 9750
59c885f7c8b413b325f17e5a4c8886cc9f4c219c tree   140 132 9763
c551f28adbcdd0da8892240b632c3613eee6a50c tree   37 47 9895
8cbe1038504cffb6ec904655779a51515d81f543 tree   140 132 9942
34f9249087d91558a478c498a4def7e0aaea72c5 blob   9 20 10074 1 4419a8c1f4dd35bb47fbd79e68b8c439df54b4ef
2922bfc1b7c3765f0e06966b731af191110127a4 tree   8 19 10094 1 8cbe1038504cffb6ec904655779a51515d81f543
b5556083f4a97bb5d46905fb2b900c05259ff250 tree   74 75 10113
b7e8fac7e3e35d93d39d2fa2260868f025a9efb4 tree   37 47 10188
non delta: 13 objects
chain length = 1: 3 objects
.git/objects/pack/pack-97bcb4e19ee5a14805411adee73372abfd76a0b0.pack: ok
$ git count-objects -v -H
count: 1
size: 4.00 KiB
in-pack: 16
packs: 1
size-pack: 11.50 KiB
prune-packable: 0
garbage: 0
size-garbage: 0 bytes
```

Identifiera den första och andra versionen av `file.py` i pack-filen och notera att den andra versionen finns i dess helhet medan den första fås av ett omvänt delta.

## Remote references

Vi kan också se att Git använder pack-filer när vi skickar objekt till en annan databas:

```bash
$ cd ..
$ git init --bare remote.git
$ ls -l remote.git/
total 24
-rw-r--r--   1 ansig  staff    21B Nov 15 19:24 HEAD
-rw-r--r--   1 ansig  staff   111B Nov 15 19:24 config
-rw-r--r--   1 ansig  staff    73B Nov 15 19:24 description
drwxr-xr-x  15 ansig  staff   480B Nov 15 19:24 hooks/
drwxr-xr-x   3 ansig  staff    96B Nov 15 19:24 info/
drwxr-xr-x   4 ansig  staff   128B Nov 15 19:24 objects/
drwxr-xr-x   4 ansig  staff   128B Nov 15 19:24 refs/
$ cd -
$ git remote add origin file://~/Scratch/remote.git
$ git push origin main
Enumerating objects: 16, done.
Counting objects: 100% (16/16), done.
Delta compression using up to 4 threads
Compressing objects: 100% (8/8), done.
Writing objects: 100% (16/16), 10.01 KiB | 10.01 MiB/s, done.
Total 16 (delta 3), reused 16 (delta 3), pack-reused 0
To file://~/Scratch/remote.git
 * [new branch]      main -> main
```

Notera att den skickade 16 objekt, alltså att den inte skickade vårt lösa objekt.

Notera också att den packade saker i en fil, men att om vi kollar i det andra repot är filerna där fortfarande opackade.
