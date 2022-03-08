# Under huven på Git

Denna presentation är en djupdykning i hur Git faktiskt fungerar. Jag kommer att prata i detalj om hur text lagras och läses i Git, och demonstrera vad som händer internt när vi kör kommandon som `checkout`, `commit` och `branch`.

Presentationen riktar sig främst till utvecklare som jobbar med Git och är intresserade att veta mer om hur det är implementerat.

Målet är att ge en djupare förståelse både för att det är intressant i sig och för att göra oss till bättre Git-användare.

Key takeaway: tänk på Git som en databas för text som vi kan hämta till vår arbetsyta

# Demos

## Objects

Initialt har vi detta:

```bash
$ git init
$ tree .git
...
```

Git är alltså en databas som lagrar objekt. Vi kan själva skapa ett sådant objekt:

```bash
$ echo "opkoko 21.2" | git hash-object -w --stdin
e4dac686ff1b71cdf9301240c529f7f40e4dcbb9
$ tree .git/objects/
.git/objects/
├── e4
│   └── dac686ff1b71cdf9301240c529f7f40e4dcbb9
├── info
└── pack
```

Git räknar ut en sha1-summa för **innehållet** (detta är viktigt, vi återkommer till det) och skapar en fil under `objects`. Filen är komprimerad, men vi kan se dess innehåll med:

```bash
$ file .git/objects/e4/dac686ff1b71cdf9301240c529f7f40e4dcbb9
.git/objects/e4/dac686ff1b71cdf9301240c529f7f40e4dcbb9: zlib compressed data
$ git cat-file -p e4dac686ff1b71cdf9301240c529f7f40e4dcbb9
opkoko 21.2
```

Det är så här Git lagrar och hämtar all data. Så säg att vi har en fil på disk som vi ändrar, då gör Git så här:

```bash
$ echo "version 1" > file1.txt
$ git hash-object -w file1.txt
83baae61804e65cc73a7201a7252750c76066a30
$ echo "version 2" > file1.txt
$ git hash-object -w file1.txt
1f7a7a472abf3dd9643fd615f6da379c4acb3e3a
$ tree .git/objects/
...
$ cat file1.txt
version 2
$ git cat-file -p 83baae61804e65cc73a7201a7252750c76066a30 > file1.txt
$ cat file1.txt
version 1
```

Alla 3 objekt vi har skapat nu är dataklumpar (`blobs`):

```bash
$ git cat-file -t 83baae61804e65cc73a7201a7252750c76066a30
blob
```

Dessa objekt innehåller dock ingen information alls om filnamnen. För detta används istället träd-objekt (`tree`). Dessa är tabeller där varje rad är en referens till ett annat objekt, antingen en data-klump eller ett annat träd. Detta representerar en nivå i en filstruktur.

Vi kan själva skapa ett sådant objekt med första versionen av vår fil:

```bash
$ git update-index --add --cacheinfo 100644 83baae61804e65cc73a7201a7252750c76066a30 file1.txt
$ git ls-files --stage
100644 83baae61804e65cc73a7201a7252750c76066a30 0	file1.txt
$ git write-tree
b7e8fac7e3e35d93d39d2fa2260868f025a9efb4
$ tree .git/objects/
...
$ git cat-file -t b7e8fac7e3e35d93d39d2fa2260868f025a9efb4
tree
$ git cat-file -p b7e8fac7e3e35d93d39d2fa2260868f025a9efb4
100644 blob 83baae61804e65cc73a7201a7252750c76066a30	file1.txt
```

Låt oss nu skapa ett till träd-objekt med andra versionen av vår fil och en ny fil:

```bash
$ git cat-file -p 1f7a7a472abf3dd9643fd615f6da379c4acb3e3a
version 2
$ git update-index --add --cacheinfo 100644 1f7a7a472abf3dd9643fd615f6da379c4acb3e3a file1.txt
$ echo "foo" > file2.txt
$ git update-index --add file2.txt # NOTERA: vi behöver inte ange --cacheinfo här utan låter Git göra det
$ git ls-files --stage
100644 1f7a7a472abf3dd9643fd615f6da379c4acb3e3a 0	file1.txt
100644 257cc5642cb1a054f08cc83f2d943e56fd3ebe99 0	file2.txt
$ git write-tree
b5556083f4a97bb5d46905fb2b900c05259ff250
$ git cat-file -t b5556083f4a97bb5d46905fb2b900c05259ff250
tree
$ git cat-file -p b5556083f4a97bb5d46905fb2b900c05259ff250
100644 blob 1f7a7a472abf3dd9643fd615f6da379c4acb3e3a	file1.txt
100644 blob 257cc5642cb1a054f08cc83f2d943e56fd3ebe99	file2.txt
```

Med träd-objekt kan vi bygga upp katalogstrukturer genom att referera andra träd. Säg att vi vill lägga en tredje fil i en katalog och att innehållet i den ska vara "version 1":

```bash
$ printf "100644 blob 83baae61804e65cc73a7201a7252750c76066a30\tfile3.txt" | git mktree # NOTERA: kom ihåg att sha-summan för innehållet är samma som "version 1"
c551f28adbcdd0da8892240b632c3613eee6a50c
$ git cat-file -p c551f28adbcdd0da8892240b632c3613eee6a50c
100644 blob 83baae61804e65cc73a7201a7252750c76066a30	file3.txt
$ git read-tree --prefix=dir1 c551f28adbcdd0da8892240b632c3613eee6a50c
$ git ls-files --stage
100644 83baae61804e65cc73a7201a7252750c76066a30 0	dir1/file3.txt
100644 1f7a7a472abf3dd9643fd615f6da379c4acb3e3a 0	file1.txt
100644 257cc5642cb1a054f08cc83f2d943e56fd3ebe99 0	file2.txt
$ git write-tree
2922bfc1b7c3765f0e06966b731af191110127a4
$ git cat-file -p 2922bfc1b7c3765f0e06966b731af191110127a4
040000 tree c551f28adbcdd0da8892240b632c3613eee6a50c	dir1
100644 blob 1f7a7a472abf3dd9643fd615f6da379c4acb3e3a	file1.txt
100644 blob 257cc5642cb1a054f08cc83f2d943e56fd3ebe99	file2.txt
```

Var är vi nu då? Jo, vi har följande:

```bash
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
├── e4
│   └── dac686ff1b71cdf9301240c529f7f40e4dcbb9
├── info
└── pack

10 directories, 8 files
```

## Commits

Låt oss börja med att skapa en förbindelse som pekar på det första träd vi skapade:

```bash
$ cp -r objects-demo/ commits-demo
$ cd commits-demo/
$ git cat-file -p b7e8fac7e3e35d93d39d2fa2260868f025a9efb4
100644 blob 83baae61804e65cc73a7201a7252750c76066a30	file1.txt
$ echo "First commit" | git commit-tree b7e8fac7e3e35d93d39d2fa2260868f025a9efb4
<COMMIT 1 SHA>
$ git cat-file -p <COMMIT 1 SHA> # OBS! Inte samma SHA på committen
tree b7e8fac7e3e35d93d39d2fa2260868f025a9efb4
author Anders Sigfridsson <anders.sigfridsson@omegapoint.se> 1636879802 +0100
committer Anders Sigfridsson <anders.sigfridsson@omegapoint.se> 1636879802 +0100

First commit
```

Varje förbindelse pekar alltså på ett träd. Varje förbindelse kan också ha en (eller fler om det är en `merge`) förälder (`parent`). Så om vi vill bygga upp en historik över alla träd vi skapat så kan vi fortsätta med:

```bash
$ git cat-file -p b5556083f4a97bb5d46905fb2b900c05259ff250
100644 blob 1f7a7a472abf3dd9643fd615f6da379c4acb3e3a	file1.txt
100644 blob 257cc5642cb1a054f08cc83f2d943e56fd3ebe99	file2.txt
$ echo "Second commit" | git commit-tree -p <COMMIT 1 SHA> b5556083f4a97bb5d46905fb2b900c05259ff250
<COMMIT 2 SHA>
$ echo "Third commit" | git commit-tree -p <COMMIT 2 SHA> 2922bfc1b7c3765f0e06966b731af191110127a4
<COMMIT 3 SHA>
$ git cat-file -p <COMMIT 3 SHA>
tree 2922bfc1b7c3765f0e06966b731af191110127a4
parent <COMMIT 2 SHA>
author Anders Sigfridsson <anders.sigfridsson@omegapoint.se> 1636880227 +0100
committer Anders Sigfridsson <anders.sigfridsson@omegapoint.se> 1636880227 +0100

Third commit
```

Nu har vi en historik och följande objekt i databasen:

```bash
$ tree .git/objects/
.git/objects/
├── 1f
│   └── 7a7a472abf3dd9643fd615f6da379c4acb3e3a
├── 25
│   └── 7cc5642cb1a054f08cc83f2d943e56fd3ebe99
├── 29
│   └── 22bfc1b7c3765f0e06966b731af191110127a4
├── 2f
│   └── 2e8c2796babefd027da63ab6cd979b5f812190
├── 66
│   └── 37401b91b0f98c1e9acb7ded97daee8009136c
├── 83
│   └── baae61804e65cc73a7201a7252750c76066a30
├── 86
│   └── 9a278f4a4a7ae04c95086ccb69af1e07fa2904
├── b5
│   └── 556083f4a97bb5d46905fb2b900c05259ff250
├── b7
│   └── e8fac7e3e35d93d39d2fa2260868f025a9efb4
├── c5
│   └── 51f28adbcdd0da8892240b632c3613eee6a50c
├── e4
│   └── dac686ff1b71cdf9301240c529f7f40e4dcbb9
├── info
└── pack

13 directories, 11 files
```

Varför är det 11 filer?

## References

```bash
$ cp -r commits-demo/ refs-demo
$ cd refs-demo/
$ git log --oneline <COMMIT 3 SHA>
869a278 Third commit
6637401 Second commit
2f2e8c2 First commit
```

Det är inte så smidigt att behöva komma ihåg checksummorna, så därför kan vi också lägga in referenser till objekt i vår databas:

```bash
$ echo "<COMMIT 3 SHA>" > .git/refs/heads/main
$ git log --oneline main
869a278 (HEAD -> main) Third commit # NOTERA: detta är vårt nuvarande HEAD
6637401 Second commit
2f2e8c2 First commit
# Det är inte uppmuntrat att vi direkt skriver till referens-filerna, utan det är bättre att använda update-ref:
$ git update-ref refs/heads/release <COMMIT 2 SHA>
$ git log --oneline release
6637401 (release) Second commit
2f2e8c2 First commit
```

Vi kan se att detta sparats som filer i `.git`-katalogen:

```bash
$ tree .git/refs/
.git/refs/
├── heads
│   ├── main
│   └── release
└── tags

2 directories, 2 files
$ cat .git/refs/heads/main
<COMMIT 3 SHA>
$ cat .git/HEAD
ref: refs/heads/main
```

Men varför i hela friden ser vårt repo ut så här?!

```bash
$ git status
On branch main
Changes not staged for commit:
  (use "git add/rm <file>..." to update what will be committed)
  (use "git restore <file>..." to discard changes in working directory)
	deleted:    dir1/file3.txt
	modified:   file1.txt

no changes added to commit (use "git add" and/or "git commit -a")
```

Jo, för att vi inte uppdaterat filerna i vår arbetsyta när vi uppdaterat förberedelseytan och databasen.

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

Vänta, var är mina refs nu då?! Vid `git gc` så paketerar Git även alla individuella filer under `refs/heads`
