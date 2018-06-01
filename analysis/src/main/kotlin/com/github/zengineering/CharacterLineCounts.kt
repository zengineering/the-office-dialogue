package com.github.zengineering

import java.io.File
import java.io.FileNotFoundException
import org.jetbrains.exposed.sql.*
import org.jetbrains.exposed.sql.transactions.transaction
import com.google.gson.Gson 
import picocli.CommandLine
import picocli.CommandLine.ParentCommand
import picocli.CommandLine.Command
import picocli.CommandLine.Option
import picocli.CommandLine.Parameters

fun countCharacterLines(dbPath: String, lineCountThreshold: Int=100): Map<String, Map<Int, Map<Int, Int>>>? {
    return try {
        var seasonalLineCounts = mutableMapOf<String, MutableMap<Int, MutableMap<Int, Int>>>()
        connectDatabase(dbPath)

        // Episode count per season per character
        val episodeCounts = transaction {
            val maxExpr = OfficeQuotes.episode.max()
            OfficeQuotes.slice(OfficeQuotes.season, maxExpr)
                .selectAll()
                .groupBy(OfficeQuotes.season)
                .orderBy(OfficeQuotes.season)
                .map { it[maxExpr]!! }
        }

        transaction {
            episodeCounts.forEachIndexed { season, epsCount ->
                (1..epsCount).forEach { eps -> 
                    OfficeQuotes
                        .slice(OfficeQuotes.speaker, OfficeQuotes.episode, OfficeQuotes.speaker.count())
                        .select { (OfficeQuotes.season eq season) and (OfficeQuotes.episode eq eps)}
                        .groupBy(OfficeQuotes.speaker)
                        .map { it[OfficeQuotes.speaker] to it[OfficeQuotes.speaker.count()] }
                        .forEach { (speaker, lineCount) ->
                            // speaker
                            seasonalLineCounts.getOrPut(speaker) { mutableMapOf<Int, MutableMap<Int, Int>>() }
                                // season
                                .getOrPut(season) { mutableMapOf<Int, Int>() }
                                //episode
                                .put(eps, lineCount)
                        }
                }
            }
        }
        seasonalLineCounts



        // Line count per season per character
        //transaction {
        //    (1..9).forEach { season -> OfficeQuotes
        //        .slice(OfficeQuotes.speaker, OfficeQuotes.speaker.count())
        //        .select { OfficeQuotes.season eq season }
        //        .groupBy(OfficeQuotes.speaker)
        //        .forEach {
        //            seasonalLineCounts.getOrPut(it[OfficeQuotes.speaker]) { mutableMapOf<Int, Int>() }
        //                .put(season, it[OfficeQuotes.speaker.count()])
        //        }
        //    }
        //}
        //seasonalLineCounts.mapValues { (_, counts) -> counts.toMap() }
        //    .filter { (_, seasons) -> seasons.values.sum() > lineCountThreshold }

    } catch (e: FileNotFoundException) {
        System.err.println("Database not found at '$dbPath'") 
        null
    }
}

@Command(
    mixinStandardHelpOptions = true, 
    name = "countCharacterLines", 
    version = arrayOf("v0.1"),
    description = arrayOf("Produce JSON of the form {character: { season : line count }} from SQLite db.")
)
class CharacterLineCounts : Runnable {
    @ParentCommand
    lateinit var parent: TheOffice

    @Option(names = arrayOf("-l", "--line-count"), description = arrayOf("Minimum threshold for total line count per character (default=100)"))
    var lineCount = 100

    override fun run() { 
        Gson().let { gson ->
            File("characterLineCounts.json").let { file ->
                countCharacterLines(this.parent.dbPath, lineCount)?.let { file.writeText(gson.toJson(it)) }
            }
        }
    }
}

fun main(args: Array<String>) = CommandLine.run(CharacterLineCounts(), *args)
