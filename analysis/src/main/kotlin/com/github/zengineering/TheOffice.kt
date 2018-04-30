package com.github.zengineering

import java.sql.DriverManager
import java.sql.Connection.TRANSACTION_SERIALIZABLE
import org.jetbrains.exposed.sql.*
import org.jetbrains.exposed.sql.transactions.transaction
import org.jetbrains.exposed.sql.transactions.ThreadLocalTransactionManager

//object OfficeQuotes: IntIdTable("office_quotes") {
object OfficeQuotes: Table("office_quotes") {
    val id = integer("id").autoIncrement().primaryKey()
    val season = integer("season")
    val episode = integer("episode")
    val scene = integer("episode")
    val speaker = text("speaker")
    val line = text("line")
    val deleted = bool("deleted")
}

fun analyze(dbPath: String) {
    Database.connect(
        { DriverManager.getConnection("jdbc:sqlite:$dbPath") }, 
        { ThreadLocalTransactionManager(it, TRANSACTION_SERIALIZABLE) }
    )

    transaction {
        OfficeQuotes.select { OfficeQuotes.id eq 1 }.singleOrNull()?.let {
            println(it[OfficeQuotes.line])
        }?: println("nothing")
    }
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

