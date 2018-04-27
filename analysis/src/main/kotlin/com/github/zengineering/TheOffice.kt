package com.github.zengineering


// Argparser
fun help(): Unit = println(
        "usage: ./TheOfficeKt <db_path>\n"
)

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

fun analyze(dbPath: String) {
    println("Hello, Kotlin")
}
