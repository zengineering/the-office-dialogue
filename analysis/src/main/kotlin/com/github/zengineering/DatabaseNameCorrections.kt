package com.github.zengineering

import org.jetbrains.exposed.sql.*
import org.jetbrains.exposed.sql.transactions.transaction

private val topLevelClass = object: Any() {}.javaClass

val nameCorrectionsCsv = "/TheOffice/name_corrections.csv"

data class Correction(val from: String, val to: String)

fun loadNameCorrections(): List<Correction> {
    val corrections = mutableListOf<Correction>()
    topLevelClass.getResourceAsStream(nameCorrectionsCsv).bufferedReader().lineSequence().forEach { line ->
        line.whenNotNullNorBlank { validLine ->
            line.split(",").let { items ->
                if (items.size == 2) {
                    corrections.add(Correction(items.first(), items.last()))
                } else {
                    System.err.println("Invalid line in csv: $validLine")
                }
            }
        }
    }
    return corrections.toList()
}

fun applyNameCorrections(corrections: List<Correction>) {
    transaction {
        corrections.forEach { (from, to) ->
            println("${from} -> ${to}")
            OfficeQuotes.update ({ OfficeQuotes.speaker eq from }) { entry ->
                entry[OfficeQuotes.speaker] = to
            }
        }
    }
}

fun correctNamesInDb(dbPath: String) {
    connectDatabase(dbPath)
    applyNameCorrections(loadNameCorrections())
}

fun main(args: Array<String>) {
    if (args.isEmpty() or args.contains("-h") or args.contains("--help")) {
        println("usage: ./correctNamesInDb <db_path>\n")
    } else { 
        correctNamesInDb(args[0])
    }
}

