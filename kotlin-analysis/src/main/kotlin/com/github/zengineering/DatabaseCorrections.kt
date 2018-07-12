package com.github.zengineering

import org.jetbrains.exposed.sql.*
import org.jetbrains.exposed.sql.transactions.transaction
import com.google.gson.Gson
import com.google.gson.reflect.TypeToken
import java.io.FileNotFoundException
import picocli.CommandLine
import picocli.CommandLine.ParentCommand
import picocli.CommandLine.Command
import picocli.CommandLine.Parameters

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

@Command(
    mixinStandardHelpOptions = true, 
    name = "correctDb", 
    version = arrayOf("v0.1"),
    description = arrayOf("Make corrections to The Office dialogue in SQLite db.")
)
class DatabaseCorrections : Runnable {
    @ParentCommand
    lateinit var parent: TheOffice

    override fun run() { 
        try {
            connectDatabase(parent.dbPath)
            applyNameCorrections(loadNameCorrections())
        } catch (e: FileNotFoundException) {
            System.err.println("Database not found at ${parent.dbPath}") 
        }
    }
}

fun main(args: Array<String>) = CommandLine.run(DatabaseCorrections(), *args)

