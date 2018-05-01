package com.github.zengineering

import java.io.File
import java.sql.DriverManager
import java.sql.Connection.TRANSACTION_SERIALIZABLE
import org.jetbrains.exposed.sql.*
import org.jetbrains.exposed.sql.transactions.transaction
import org.jetbrains.exposed.sql.transactions.ThreadLocalTransactionManager

//object OfficeQuotes: IntIdTable("office_quotes") {
object OfficeQuotes: Table("office_quotes") {
    val id: Column<Int> = integer("id").autoIncrement().primaryKey()
    val season: Column<Int> = integer("season")
    val episode: Column<Int> = integer("episode")
    val scene: Column<Int> = integer("episode")
    val speaker: Column<String> = text("speaker")
    val line: Column<String> = text("line")
    val deleted: Column <Boolean> = bool("deleted")
}

data class Correction(val from: String, val to: String)

fun <R> String?.whenNotNullNorBlank(block: (String) -> R): R? {
    return this?.let { receiver ->
        if (receiver.isNotBlank()) {
            block(receiver)
        } else null
    }
}

fun checkFile(path: String): String? {
    val absolutePath = File(path).getAbsoluteFile()
    return if (absolutePath.exists()) {
        absolutePath.path
    } else {
        null
    }
}

fun initDbConnection(dbPath: String) {
    Database.connect(
        { DriverManager.getConnection("jdbc:sqlite:$dbPath") }, 
        { ThreadLocalTransactionManager(it, TRANSACTION_SERIALIZABLE) }
    )
}

fun readNameCorrections(csv: String): List<Correction> {
    val corrections = mutableListOf<Correction>()
    checkFile(csv)?.let { validCsv -> 
            File(validCsv).forEachLine { line ->
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
    }
    ?: System.err.println("Invalid corrections file: $csv")
    return corrections.toList()
}

fun applyNameCorrections(dbPath: String, corrections: List<Correction>) {
    checkFile(dbPath)?.let { validDbPath ->
        initDbConnection(validDbPath)

        transaction {
            corrections.forEach { (from, to) ->
                println("${from} -> ${to}")
                OfficeQuotes.update ({ OfficeQuotes.speaker eq from }) { entry ->
                    entry[OfficeQuotes.speaker] = to
                }
            }
        }
    }
    ?: System.err.println("Invalid database path: $dbPath")
}

// Argparser
fun help(): Unit = println("usage: ./TheOfficeKt <db_path>\n")

fun main(args: Array<String>) {
    if (args.isNotEmpty()) {
        if (args.contains("-h") or args.contains("--help")) {
            help()
        } else { 
            val corrections = readNameCorrections(args[1])
            applyNameCorrections(args[0], corrections)
        }
    } else {
        help()
    }
}


