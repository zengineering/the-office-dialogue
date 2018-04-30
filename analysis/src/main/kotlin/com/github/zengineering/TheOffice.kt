package com.github.zengineering

import java.io.File
import java.sql.DriverManager
import java.sql.Connection.TRANSACTION_SERIALIZABLE
import org.jetbrains.exposed.sql.*
import org.jetbrains.exposed.sql.transactions.transaction
import org.jetbrains.exposed.sql.transactions.ThreadLocalTransactionManager
import kotlin.reflect.full.*

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

fun analyze(dbPath: String) {
    checkFile(dbPath)?.let { validDbPath ->
        initDbConnection(validDbPath)

        transaction {
            //val speakers = OfficeQuotes
            //    .slice(OfficeQuotes.speaker)
            //    .selectAll()
            //    .withDistinct()

            OfficeQuotes.slice(OfficeQuotes.id.count(), OfficeQuotes.speaker)
                .selectAll()
                .groupBy(OfficeQuotes.speaker).apply {
                    this.first().javaClass.kotlin.run {
                        this.memberProperties.forEach { println(it.name) }
                        this.memberFunctions.forEach { println(it.name) }
                    }
                }
                .forEach { println(it) }

        }
    }
    ?: System.err.println("Invalid database path: $dbPath")
}

// Argparser
fun help(): Unit = println("usage: ./TheOfficeKt <db_path>\n")

fun main(args: Array<String>) {
    if (args.isNotEmpty()) {
        when (args[0]) {
            "-h", "--help" -> help()
            else -> { 
                analyze(args[0]); 
            }
        }
    } else {
        help()
    }
}

