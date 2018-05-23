package com.github.zengineering

import java.sql.DriverManager
import java.sql.Connection.TRANSACTION_SERIALIZABLE
import org.jetbrains.exposed.sql.*
import org.jetbrains.exposed.sql.transactions.ThreadLocalTransactionManager
import java.io.FileNotFoundException

object OfficeQuotes: Table("office_quotes") {
    val id: Column<Int> = integer("id").autoIncrement().primaryKey()
    val season: Column<Int> = integer("season")
    val episode: Column<Int> = integer("episode")
    val scene: Column<Int> = integer("episode")
    val speaker: Column<String> = text("speaker")
    val line: Column<String> = text("line")
    val deleted: Column <Boolean> = bool("deleted")
}

@Throws(FileNotFoundException::class)
fun connectDatabase(dbPath: String) {
    checkFileError(dbPath)?.let { validDbPath ->
        Database.connect(
            { DriverManager.getConnection("jdbc:sqlite:$validDbPath") }, 
            { ThreadLocalTransactionManager(it, TRANSACTION_SERIALIZABLE) }
        )
    }
}

