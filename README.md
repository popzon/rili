# rili

点滴日历（改版「日历」）的放假/调休数据源。

- 数据来自 [holiday-cn](https://github.com/NateScarlet/holiday-cn)
- `api/getallconfig.ashx` 是 App 读取的文件，GitHub Actions 每天检查一次，有新数据才更新
- App 通过 jsDelivr 读取：`https://cdn.jsdelivr.net/gh/<用户名>/rili@main/api/getallconfig.ashx`
