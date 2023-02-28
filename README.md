# GALEN

TODO

## Usage

```console
me@box:~$ galen profile list
default
dev

# create a new profile
me@box:~$ galen profile new prd --endpoint https://production-elastic.com
Created profile 'prd'

me@box:~$ # create a new profile with auth from stdin
me@box:~$ galen profile new prd --endpoint https://prd-elastic.com --auth-from-stdin < production-basic-auth
Created profile 'prd'

me@box:~$ # tail for logs containing the text "request error"
me@box:~$ galen --profile prd tail "request error"
2023-02-27T19:42:53Z obtained request error from API

me@box:~$ # search for logs containing the text "request error" for yesterday
me@box:~$ galen --profile prd search --since yesterday --until today "request error"
2023-02-25T19:41:52Z parsing request error 500 from server
```
