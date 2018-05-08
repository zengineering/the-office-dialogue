package com.github.zengineering

import org.jetbrains.exposed.sql.*
import org.jetbrains.exposed.sql.transactions.transaction

fun countLinesPerCharacter(dbPath: String) {
    connectDatabase(dbPath)
    transaction {
        (1..9).forEach { season ->
            OfficeQuotes
                .slice(OfficeQuotes.speaker)
                .select { OfficeQuotes.season eq season }
                .groupingBy { it[OfficeQuotes.speaker] }
                .eachCount()
                .toList()
                .sortedByDescending { (_, count) -> count }
        }
    }
}


fun main(args: Array<String>) {
    if (args.isEmpty() or args.contains("-h") or args.contains("--help")) {
        println("usage: ./CharacterLineCountsKt <db_path>\n")
    } else { 
        countLinesPerCharacter(args[0])
    }
}
