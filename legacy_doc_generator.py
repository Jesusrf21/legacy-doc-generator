# legacy_doc_generator.py

import os
import ast
import javalang
from pathlib import Path
import streamlit as st
from io import StringIO, BytesIO
from datetime import datetime
from markdown import markdown
from xhtml2pdf import pisa

def extract_python_classes_and_functions(code):
    tree = ast.parse(code)
    classes = []
    functions = []
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            name = node.name
            docstring = ast.get_docstring(node) or "No docstring"
            functions.append((name, docstring))
        elif isinstance(node, ast.ClassDef):
            class_name = node.name
            methods = []
            for item in node.body:
                if isinstance(item, ast.FunctionDef):
                    method_name = item.name
                    doc = ast.get_docstring(item) or "No docstring"
                    methods.append((method_name, doc))
            classes.append((class_name, methods))
    return classes, functions

def extract_java_elements(code):
    classes = []
    try:
        tree = javalang.parse.parse(code)
        for _, node in tree.filter(javalang.tree.ClassDeclaration):
            class_name = node.name
            method_summaries = []
            for method in node.methods:
                method_name = method.name
                method_summaries.append((method_name, "No docstring (Java)"))
            classes.append((class_name, method_summaries))
    except:
        pass
    return classes

def summarize_python_structure(py_classes, functions):
    parts = []
    if py_classes:
        parts.append(f"{len(py_classes)} clases: " + ", ".join([c[0] for c in py_classes]))
    if functions:
        parts.append(f"{len(functions)} funciones: " + ", ".join([f[0] for f in functions]))
    return "Archivo con " + "; ".join(parts) + "." if parts else "Archivo sin clases ni funciones."

def summarize_java_structure(classes):
    if not classes:
        return "No se encontraron clases Java en el archivo."
    resumen = f"Archivo con {len(classes)} clases detectadas:\n"
    for class_name, methods in classes:
        resumen += f"- Clase `{class_name}` con {len(methods)} métodos.\n"
    return resumen

def generar_markdown(nombre_archivo, resumen, detalles):
    md = StringIO()
    md.write(f"# Documentación generada para `{nombre_archivo}`\n\n")
    md.write(f"**Fecha:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
    md.write(f"## 🧠 Resumen general\n{resumen}\n\n")
    md.write("## 🔍 Detalles\n")
    for bloque in detalles:
        md.write(bloque + "\n\n")
    return md.getvalue()

def convertir_pdf(md_text):
    html = markdown(md_text)
    pdf_bytes = BytesIO()
    pisa.CreatePDF(src=html, dest=pdf_bytes)
    return pdf_bytes.getvalue()

# Streamlit UI
st.title("🧠 Generador de Documentación Técnica para Código Legacy")

uploaded_file = st.file_uploader("Sube un archivo de código fuente (.py o .java)", type=["py", "java"])

if uploaded_file is not None:
    code = uploaded_file.read().decode("utf-8")
    st.subheader("📄 Código fuente")
    extension = uploaded_file.name.split(".")[-1]
    st.code(code, language="java" if extension == "java" else "python")

    st.subheader("🧠 Resumen general del archivo")
    markdown_blocks = []
    if extension == "py":
        py_classes, functions = extract_python_classes_and_functions(code)
        summary = summarize_python_structure(py_classes, functions)
        st.text(summary)
        markdown_blocks.append(f"{summary}")

        st.subheader("🏛️ Clases y métodos detectados (Python)")
        for class_name, methods in py_classes:
            block = f"### Clase: `{class_name}`\n"
            st.markdown(f"### Clase: `{class_name}`")
            for method_name, docstring in methods:
                st.markdown(f"- Método: `{method_name}` — {docstring}")
                block += f"- Método: `{method_name}` — {docstring}\n"
            markdown_blocks.append(block)

        st.subheader("🔍 Funciones detectadas (Python)")
        block = ""
        for name, docstring in functions:
            st.markdown(f"**Función:** `{name}`")
            st.markdown(f"> {docstring}")
            block += f"**Función:** `{name}`\n> {docstring}\n"
        markdown_blocks.append(block)

    elif extension == "java":
        java_classes = extract_java_elements(code)
        summary = summarize_java_structure(java_classes)
        st.text(summary)
        markdown_blocks.append(f"{summary}")

        st.subheader("🔍 Clases y métodos detectados (Java)")
        for class_name, methods in java_classes:
            block = f"### Clase: `{class_name}`\n"
            st.markdown(f"### Clase: `{class_name}`")
            for method_name, docstring in methods:
                st.markdown(f"- Método: `{method_name}` — {docstring}")
                block += f"- Método: `{method_name}` — {docstring}\n"
            markdown_blocks.append(block)

    st.subheader("📤 Exportar documentación")
    markdown_text = generar_markdown(uploaded_file.name, summary, markdown_blocks)
    st.download_button("📄 Descargar como Markdown", markdown_text.encode("utf-8"), file_name="documentacion.md")

    pdf_file = convertir_pdf(markdown_text)
    st.download_button("📄 Descargar como PDF", pdf_file, file_name="documentacion.pdf")
