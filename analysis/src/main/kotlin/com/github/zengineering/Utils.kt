package com.github.zengineering

import java.io.File

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

