# GALEN

TODO

## Usage

```console
me@box:~$ galen profile list
default
dev

me@box:~$ # create a new profile
me@box:~$ galen profile new prd --endpoint https://prd-elastic.com
Created profile 'prd'.

me@box:~$ # tail for logs containing the text "request error"
me@box:~$ galen --profile prd tail "request error"
2023-02-27T19:42:53.643Z - obtained request error from API

me@box:~$ # search for logs containing the text "request error" for yesterday
me@box:~$ galen --profile prd search --since yesterday --until today "request error"
2023-02-25T19:41:52Z parsing request error 500 from server

me@box:~$ # create a new profile with auth by passing password from stdin
me@box:~$ galen profile new prd --endpoint https://prd-elastic.com --user foo --password < pass-file
Created profile 'prd'.

me@box:~$ # set profile as default
me@box:~$ galen profile set-default prd
Profile 'prd' is now the default profile.

me@box:~$ # update an existing profile
me@box:~$ galen profile update prd --delta 60
Updated profile 'prd'.
```
