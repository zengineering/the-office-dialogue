package com.github.zengineering

import org.jetbrains.exposed.sql.*
import org.jetbrains.exposed.sql.transactions.transaction
import java.io.File
import com.google.gson.Gson
import java.io.FileNotFoundException

fun countSeasonalLines(dbPath: String) {
    var seasonalLineCounts = mutableMapOf<String, MutableMap<Int, Int>>()
    try {
        connectDatabase(dbPath)
        transaction {
            (1..9).forEach { season -> OfficeQuotes
                .slice(OfficeQuotes.speaker, OfficeQuotes.speaker.count())
                .select { OfficeQuotes.season eq season }
                .groupBy(OfficeQuotes.speaker)
                .forEach {
                    seasonalLineCounts.getOrPut(it[OfficeQuotes.speaker]) { mutableMapOf<Int, Int>() }
                        .put(season, it[OfficeQuotes.speaker.count()])
                 }
            }
        }
        Gson().run { File("seasonalLineCount.json").writeText(this.toJson(
            seasonalLineCounts.filter { (_, seasons) -> seasons.values.sum() > 100 }
        )) }
    } catch (e: FileNotFoundException) {
        System.err.println("Database not found at $dbPath") 
    }
}


fun main(args: Array<String>) {
    if (args.isEmpty() or args.contains("-h") or args.contains("--help")) {
        println("usage: ./CharacterLineCountsKt <db_path>\n")
    } else { 
        countSeasonalLines(args[0])
    }
}
