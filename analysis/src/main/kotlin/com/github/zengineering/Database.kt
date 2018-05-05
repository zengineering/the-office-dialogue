package com.github.zengineering

import java.sql.DriverManager
import java.sql.Connection.TRANSACTION_SERIALIZABLE
import org.jetbrains.exposed.sql.*
import org.jetbrains.exposed.sql.transactions.ThreadLocalTransactionManager

object OfficeQuotes: Table("office_quotes") {
    val id: Column<Int> = integer("id").autoIncrement().primaryKey()
    val season: Column<Int> = integer("season")
    val episode: Column<Int> = integer("episode")
    val scene: Column<Int> = integer("episode")
    val speaker: Column<String> = text("speaker")
    val line: Column<String> = text("line")
    val deleted: Column <Boolean> = bool("deleted")
}


fun initDbConnection(dbPath: String) {
    Database.connect(
        { DriverManager.getConnection("jdbc:sqlite:$dbPath") }, 
        { ThreadLocalTransactionManager(it, TRANSACTION_SERIALIZABLE) }
    )
}

