package com.github.zengineering

import java.io.File
import java.io.FileNotFoundException
import org.jetbrains.exposed.sql.*
import org.jetbrains.exposed.sql.transactions.transaction
import com.google.gson.Gson
import picocli.CommandLine
import picocli.CommandLine.Command
import picocli.CommandLine.Option
import picocli.CommandLine.Parameters

fun countSeasonalLines(dbPath: String, lineCountThreshold: Int=100) {
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
            seasonalLineCounts.filter { (_, seasons) -> seasons.values.sum() > lineCountThreshold }
        )) }
    } catch (e: FileNotFoundException) {
        System.err.println("Database not found at '$dbPath'") 
    }
}

@Command(
    mixinStandardHelpOptions = true, 
    name = "CharacterLineCounts", 
    version = arrayOf("v0.1"),
    description = arrayOf("Produce JSON of the form {character: { season : line count }} from SQLite db.")
)
class CharacterLineCounts : Runnable {
    @Option(names = arrayOf("-l", "--line-count"), description = arrayOf("Minimum threshold for total line count per character"))
    var lineCount = 100

    @Parameters(index = "0", paramLabel = "DB_PATH", description = arrayOf("Path to SQLite quotes database"))
    var dbPath: String = ""

    override fun run() = countSeasonalLines(dbPath, lineCount)
}

fun main(args: Array<String>) = CommandLine.run(CharacterLineCounts(), *args)
