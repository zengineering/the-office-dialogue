package com.github.zengineering

import org.jetbrains.exposed.sql.*
import org.jetbrains.exposed.sql.transactions.transaction
import com.google.gson.Gson
import com.google.gson.reflect.TypeToken
import java.io.FileNotFoundException

private val topLevelClass = object: Any() {}.javaClass

val nameCorrectionsCsv = "/TheOffice/name_corrections.json"

fun loadNameCorrections(): Map<String, String> {
    return topLevelClass.getResourceAsStream(nameCorrectionsCsv).use { 
        it.reader().let { jsonReader -> 
            Gson().fromJson<Map<String, String>>(jsonReader, 
                object: TypeToken<Map<String, String>>() {}.type) 
        }
    }
}

fun applyNameCorrections(corrections: Map<String, String>) {
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
    try {
        connectDatabase(dbPath)
        applyNameCorrections(loadNameCorrections())
    } catch (e: FileNotFoundException) {
        System.err.println("Database not found at $dbPath") 
    }
}

fun main(args: Array<String>) {
    if (args.isEmpty() or args.contains("-h") or args.contains("--help")) {
        println("usage: ./correctNamesInDb <db_path>\n")
    } else { 
        correctNamesInDb(args[0])
    }
}

