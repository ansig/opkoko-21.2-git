# Blobs

83baae61804e65cc73a7201a7252750c76066a30    "version 1"
1f7a7a472abf3dd9643fd615f6da379c4acb3e3a    "version 2"
257cc5642cb1a054f08cc83f2d943e56fd3ebe99    "foo"

# Trees

b7e8fac7e3e35d93d39d2fa2260868f025a9efb4
100644 blob 83baae61804e65cc73a7201a7252750c76066a30	file1.txt

b5556083f4a97bb5d46905fb2b900c05259ff250
100644 blob 1f7a7a472abf3dd9643fd615f6da379c4acb3e3a	file1.txt
100644 blob 257cc5642cb1a054f08cc83f2d943e56fd3ebe99	file2.txt

c551f28adbcdd0da8892240b632c3613eee6a50c
100644 blob 83baae61804e65cc73a7201a7252750c76066a30	file3.txt

2922bfc1b7c3765f0e06966b731af191110127a4
040000 tree c551f28adbcdd0da8892240b632c3613eee6a50c	dir1
100644 blob 1f7a7a472abf3dd9643fd615f6da379c4acb3e3a	file1.txt
100644 blob 257cc5642cb1a054f08cc83f2d943e56fd3ebe99	file2.txt

# Commits

echo "First commit" | git commit-tree b7e8fac7e3e35d93d39d2fa2260868f025a9efb4
echo "Second commit" | git commit-tree -p <COMMIT 1 SHA> b5556083f4a97bb5d46905fb2b900c05259ff250
echo "Third commit" | git commit-tree -p <COMMIT 2 SHA> 2922bfc1b7c3765f0e06966b731af191110127a4
