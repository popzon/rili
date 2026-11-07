# rili

点滴日历（改版「日历」）的放假/调休数据源。

- 数据来自 [holiday-cn](https://github.com/NateScarlet/holiday-cn)
- `api/getallconfig.ashx` 是 App 读取的文件，GitHub Actions 每天检查一次，有新数据才更新
- App 通过 jsDelivr 读取：`https://cdn.jsdelivr.net/gh/popzon/rili@main/api/getallconfig.ashx`
- 美国节假日（金恩日、总统日、复活节、阵亡将士纪念日、六月节、独立日、劳工节、哥伦布日、老兵节、黑五）按年份算好写在 Festival 的 Y 表里，需要配套的「美国节假日」版 App
