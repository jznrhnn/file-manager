[简体中文](README_CN.md) | [English](README.md)

本项目用于管理 GTA V（Grand Theft Auto V） 的游戏文件，快速切换原始游戏文件和 Mod 游戏文件，确保在进行在线模式时游戏文件是未修改过的，但理论上也可以用于管理其他文件夹。

### 使用说明

1. **修改配置文件**：将 `game_path` 替换为你的游戏文件路径，将 `backup_path` 替换为你想要保存备份路径（可选）。

2. **运行 `mainUI.py`**：

   1. **Record Origin Game File**（确保运行前游戏是干净的）：这将生成 `origin_list.json`，记录当前游戏文件，默认文件是我 GTAV 游戏文件的列表。
   2. **根据 mod 需要更改文件**：添加的文件会展示为绿色，被删除的为红色，被修改与源文件不同的橙色。你可以随时通过 **Show Difference** 查看当前游戏文件和原始文件的区别
   3. **Restore Origin Game File**：使用文件记录还原原始游戏文件（此操作将备份你的模组并还原游戏文件）。
   4. **Load Mod File**：重新加载你的备份文件。
