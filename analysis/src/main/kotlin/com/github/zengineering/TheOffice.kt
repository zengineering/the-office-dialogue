package com.github.zengineering

import picocli.CommandLine
import picocli.CommandLine.Parameters
import picocli.CommandLine.RunAll
import picocli.CommandLine.Command

@Command(
    mixinStandardHelpOptions = true, 
    name = "theOffice", 
    version = arrayOf("v0.1"),
    description = arrayOf("Run commands related to The Office dialogue in a SQLite database"),
    subcommands = arrayOf(CharacterLineCounts::class, DatabaseCorrections::class)
)
class TheOffice : Runnable {
    @Parameters(index = "0", paramLabel = "DB_PATH", description = arrayOf("Path to SQLite quotes database"))
    var dbPath: String = ""

    override fun run() = CommandLine(this).usage(System.out)
}

fun main(args: Array<String>) {
    CommandLine(TheOffice())
        //.addSubcommand("correctDb", DatabaseCorrections())
        //.addSubcommand("countCharacterLines", CharacterLineCounts())
        .parseWithHandler(RunAll(), args)
}


