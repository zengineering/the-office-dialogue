package com.github.zengineering

import org.jetbrains.exposed.sql.*
import org.jetbrains.exposed.sql.transactions.transaction
import java.io.File
import com.google.gson.Gson

fun countLinesPerCharacter(dbPath: String) {
    var characterLineCounts = mapOf<Int, Map<String, Int>>()
    connectDatabase(dbPath)
    transaction {
        characterLineCounts = (1..9).associateBy(
            { it },
            { season -> OfficeQuotes
                .slice(OfficeQuotes.speaker, OfficeQuotes.speaker.count())
                .select { OfficeQuotes.season eq season }
                .groupBy(OfficeQuotes.speaker)
                .associateBy(
                    { it[OfficeQuotes.speaker] },
                    { it[OfficeQuotes.speaker.count()] }
                )
            }
        )
    }
    Gson().run { File("characterLineCount.json").writeText(this.toJson(characterLineCounts)) }
}


fun main(args: Array<String>) {
    if (args.isEmpty() or args.contains("-h") or args.contains("--help")) {
        println("usage: ./CharacterLineCountsKt <db_path>\n")
    } else { 
        countLinesPerCharacter(args[0])
    }
}
