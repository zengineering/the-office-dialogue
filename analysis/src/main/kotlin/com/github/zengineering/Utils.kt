package com.github.zengineering

import java.io.File

inline fun <R> String?.whenNotNullNorBlank(action: (String) -> R): R? {
    return this?.let { receiver ->
        if (receiver.isNotBlank()) {
            action(receiver)
        } else null
    }
}

inline fun <R: Any, E: Any, T:Collection<E>> T?.whenNotNullNorEmpty(action: (T) -> R): R? {
    return this?.let { receiver ->
        if (receiver.isNotEmpty()) {
            action(receiver)
        } else null
    }
}

fun checkFile(path: String): String? {
    val absolutePath = File(path).getAbsoluteFile()
    return if (absolutePath.exists()) {
        absolutePath.path
    } else null
}

