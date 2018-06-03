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

/**
 * Count the number of lines spoken by each character in each episode
 *
 * @param dbPath Path to database with dialogue
 * @param lineCountThreshold The minimum number of lines required to include a character
 * @return Line counts in the form of character -> season -> episode -> line count
 *
**/
fun countCharacterLines(dbPath: String, lineCountThreshold: Int=100): Map<String, Map<Int, Map<Int, Int>>>? {
    return try {
        var characterLineCounts = mutableMapOf<String, MutableMap<Int, MutableMap<Int, Int>>>()
        connectDatabase(dbPath)

        // Episode count per season
        val episodeCounts = transaction {
            val maxExpr = OfficeQuotes.episode.max()
            // SELECT season, MAX(episode)
            OfficeQuotes.slice(OfficeQuotes.season, maxExpr)
                .selectAll()
                // get all seasons
                .groupBy(OfficeQuotes.season)
                // sort by season to store in list
                .orderBy(OfficeQuotes.season)
                // extract the max(episode)
                .map { it[maxExpr]!! }
        }

        transaction {
            // for each episode in each season, count the number of lines by each character
            // The current method could be improved, but it allows for explicit results 
            //   (and manual corrections of the json)
            (1..9).zip(episodeCounts).forEach { (season, epsCount) ->
                (1..epsCount).forEach { eps -> 
                    OfficeQuotes
                        // SELECT speaker, episode, number of lines (speaker.count)
                        .slice(OfficeQuotes.speaker, OfficeQuotes.episode, OfficeQuotes.speaker.count())
                        // filter by season and episode
                        .select { (OfficeQuotes.season eq season) and (OfficeQuotes.episode eq eps)}
                        // group by speaker
                        .groupBy(OfficeQuotes.speaker)
                        // extract speaker ans line count
                        .map { it[OfficeQuotes.speaker] to it[OfficeQuotes.speaker.count()] }
                        .forEach { (speaker, lineCount) ->
                            // get/insert speaker
                            characterLineCounts.getOrPut(speaker) { mutableMapOf<Int, MutableMap<Int, Int>>() }
                                // get/insert season
                                .getOrPut(season) { mutableMapOf<Int, Int>() }
                                // get/insert episode
                                .put(eps, lineCount)
                        }
                }
            }
        }

        // filter by total line count
        characterLineCounts.filter { (_, seasonCounts) ->
            seasonCounts.values.sumBy { it.values.sum() } > lineCountThreshold
        }

    } catch (e: FileNotFoundException) {
        System.err.println("Database not found at '$dbPath'") 
        null
    }
}

@Command(
    mixinStandardHelpOptions = true, 
    name = "countCharacterLines", 
    version = arrayOf("v0.2"),
    description = arrayOf("Produce JSON of the form {character: { season : line count }} from SQLite db.")
)
class CharacterLineCounts : Runnable {
    @ParentCommand
    lateinit var parent: TheOffice

    @Option(names = arrayOf("-l", "--line-count"), description = arrayOf("Minimum threshold for total line count per character (default=100)"))
    var lineCount = 100

    // Get line counts per character; convert to json; write to file
    override fun run() { 
        Gson().let { gson ->
            File("characterLineCounts.json").let { file ->
                countCharacterLines(this.parent.dbPath, lineCount)?.let { file.writeText(gson.toJson(it)) }
            }
        }
    }
}

fun main(args: Array<String>) = CommandLine.run(CharacterLineCounts(), *args)
