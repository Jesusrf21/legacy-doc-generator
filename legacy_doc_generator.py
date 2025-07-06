import os
import ast
import javalang
from pathlib import Path
import streamlit as st
from io import StringIO, BytesIO
from datetime import datetime
from markdown import markdown
from xhtml2pdf import pisa
import zipfile
import astor
from codigo_mejorado_ai import mejorar_codigo_con_docstrings

# ------------------------
# EXTRACCIÓN Y ANÁLISIS
# ------------------------

def extract_python_classes_and_functions(code):
    tree = ast.parse(code)
    classes = []
    functions = []
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            name = node.name
            docstring = ast.get_docstring(node) or "No docstring"
            functions.append((name, docstring, node))
        elif isinstance(node, ast.ClassDef):
            class_name = node.name
            methods = []
            for item in node.body:
                if isinstance(item, ast.FunctionDef):
                    method_name = item.name
                    doc = ast.get_docstring(item) or "No docstring"
                    methods.append((method_name, doc, item))
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
                has_doc = bool(method.documentation)
                method_summaries.append((method_name, has_doc))
            classes.append((class_name, method_summaries))
    except:
        pass
    return classes

# ------------------------
# RESÚMENES Y MÉTRICAS
# ------------------------

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

def contar_lineas_codigo(code):
    return sum(1 for line in code.splitlines() if line.strip())

def obtener_métricas_python(code, clases, functions):
    lineas = contar_lineas_codigo(code)
    total_clases = len(clases)
    total_funciones = len(functions)
    sin_docstring = sum(1 for _, doc, _ in functions if doc == "No docstring")
    sin_docstring += sum(1 for _, métodos in clases for _, doc, _ in métodos if doc == "No docstring")
    largos = sum(1 for _, métodos in clases for _, _, nodo in métodos if hasattr(nodo, 'body') and len(nodo.body) > 20)
    return {
        "📄 Líneas de código": lineas,
        "🏛️ Clases": total_clases,
        "🛠️ Funciones/Métodos": total_funciones,
        "⚠️ Sin docstring": sin_docstring,
        "📏 Métodos largos": largos,
    }

def obtener_métricas_java(code, clases):
    lineas = contar_lineas_codigo(code)
    total_clases = len(clases)
    total_metodos = sum(len(metodos) for _, metodos in clases)
    sin_docstring = sum(1 for _, metodos in clases for _, tiene_doc in metodos if not tiene_doc)
    return {
        "📄 Líneas de código": lineas,
        "🏛️ Clases": total_clases,
        "🛠️ Métodos": total_metodos,
        "⚠️ Sin documentación": sin_docstring,
    }

# ------------------------
# DETECCIÓN DE MALAS PRÁCTICAS Y SUGERENCIAS
# ------------------------

def detect_smells_python(py_classes, functions):
    issues = []
    for fname, docstring, node in functions:
        if docstring == "No docstring":
            issues.append(f"Función `{fname}` sin docstring.")
    for cname, methods in py_classes:
        if len(methods) == 0:
            issues.append(f"Clase `{cname}` sin métodos.")
        for mname, doc, node in methods:
            if doc == "No docstring":
                issues.append(f"Método `{mname}` en clase `{cname}` sin docstring.")
            if hasattr(node, 'body') and len(node.body) > 20:
                issues.append(f"Método `{mname}` en clase `{cname}` es muy largo (>20 líneas).")
    return issues

def detect_smells_java(java_classes):
    issues = []
    for class_name, methods in java_classes:
        if len(methods) == 0:
            issues.append(f"Clase `{class_name}` sin métodos.")
        for method_name, has_doc in methods:
            if not has_doc:
                issues.append(f"Método `{method_name}` en clase `{class_name}` sin documentación.")
    return issues

def sugerencias_mejoras(smells):
    mejoras = []
    for problema in smells:
        if "sin docstring" in problema or "sin documentación" in problema:
            mejoras.append("✍️ Añade un docstring que explique la funcionalidad del método o función.")
        elif "muy largo" in problema:
            mejoras.append("🔧 Divide el método en varias funciones más pequeñas para mejorar la legibilidad.")
        elif "sin métodos" in problema:
            mejoras.append("📐 Revisa si la clase necesita lógica interna o puede ser convertida en una estructura de datos.")
        else:
            mejoras.append("💡 Revisa este fragmento para aplicar buenas prácticas.")
    return list(set(mejoras))

# ------------------------
# EXPORTACIÓN
# ------------------------

def generar_markdown(nombre_archivo, resumen, detalles, smells):
    md = StringIO()
    md.write(f"# Documentación generada para `{nombre_archivo}`\n\n")
    md.write(f"**Fecha:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
    md.write(f"## 🧠 Resumen general\n{resumen}\n\n")
    md.write("## 🔍 Detalles\n")
    for bloque in detalles:
        md.write(bloque + "\n\n")
    if smells:
        md.write("## 🚨 Malas prácticas detectadas\n")
        for smell in smells:
            md.write(f"- {smell}\n")
    return md.getvalue()

def convertir_pdf(md_text):
    html = markdown(md_text)
    pdf_bytes = BytesIO()
    pisa.CreatePDF(src=html, dest=pdf_bytes)
    return pdf_bytes.getvalue()


# ------------------------
# RESÚMENES NATURALES EN LENGUAJE NATURAL
# ------------------------

def generar_resumen_natural(nombre_archivo, extension, resumen, metricas, smells):
    partes = [f"🔎 Análisis del archivo `{nombre_archivo}`:"]
    if extension == "py":
        clases = metricas.get("🏛️ Clases", 0)
        funcs = metricas.get("🛠️ Funciones/Métodos", 0)
        docstring_faltantes = metricas.get("⚠️ Sin docstring", 0)
        largos = metricas.get("📏 Métodos largos", 0)
        partes.append(f"Este archivo contiene {clases} clases y {funcs} funciones o métodos.")
        if docstring_faltantes > 0:
            partes.append(f"Se detectaron {docstring_faltantes} funciones o métodos sin docstring.")
        if largos > 0:
            partes.append(f"También hay {largos} métodos que superan las 20 líneas de longitud.")
        if not smells:
            partes.append("No se detectaron malas prácticas evidentes.")
        else:
            partes.append("Se recomienda revisar el estilo y la documentación de algunos elementos.")

    elif extension == "java":
        clases = metricas.get("🏛️ Clases", 0)
        metodos = metricas.get("🛠️ Métodos", 0)
        sin_docs = metricas.get("⚠️ Sin documentación", 0)
        partes.append(f"Este archivo contiene {clases} clases con un total de {metodos} métodos.")
        if sin_docs > 0:
            partes.append(f"Se encontraron {sin_docs} métodos sin documentación.")
        if not smells:
            partes.append("Todo parece estar bien documentado y estructurado.")
        else:
            partes.append("Sería conveniente documentar mejor algunos métodos.")

    return " ".join(partes)

# ------------------------
# STREAMLIT APP
# ------------------------

st.title("🧠 Generador de Documentación Técnica para Código Legacy")

uploaded_file = st.file_uploader("Sube un archivo (.py, .java o .zip)", type=["py", "java", "zip"])

if uploaded_file is not None:
    archivos = []

    if uploaded_file.name.endswith(".zip"):
        with zipfile.ZipFile(uploaded_file) as z:
            for file_info in z.infolist():
                if file_info.filename.endswith((".py", ".java")):
                    with z.open(file_info) as f:
                        code = f.read().decode("utf-8")
                        archivos.append((file_info.filename, code))
        if not archivos:
            st.warning("El archivo ZIP no contiene ningún archivo .py ni .java válido.")
            st.stop()
    else:
        code = uploaded_file.read().decode("utf-8")
        archivos.append((uploaded_file.name, code))

    for filename, code in archivos:
        st.divider()
        st.subheader(f"📁 Archivo: `{filename}`")
        extension = filename.split(".")[-1]
        st.code(code, language="java" if extension == "java" else "python")

        markdown_blocks = []
        smells = []

        if extension == "py":
            py_classes, functions = extract_python_classes_and_functions(code)
            summary = summarize_python_structure(py_classes, functions)
            st.text(summary)
            markdown_blocks.append(f"{summary}")

            st.subheader("📊 Métricas del archivo")
            metricas = obtener_métricas_python(code, py_classes, functions)
            for clave, valor in metricas.items():
                st.markdown(f"**{clave}:** {valor}")
            if st.button(f"📊 Ver gráfico de métricas ({filename})"):
                st.bar_chart(data={k: [v] for k, v in metricas.items()})

            st.subheader("🏛️ Clases y métodos detectados (Python)")
            for class_name, methods in py_classes:
                block = f"### Clase: `{class_name}`\n"
                st.markdown(f"### Clase: `{class_name}`")
                for method_name, docstring, _ in methods:
                    st.markdown(f"- Método: `{method_name}` — {docstring}")
                    block += f"- Método: `{method_name}` — {docstring}\n"
                markdown_blocks.append(block)

            st.subheader("🔍 Funciones detectadas (Python)")
            block = ""
            for name, docstring, _ in functions:
                st.markdown(f"**Función:** `{name}`")
                st.markdown(f"> {docstring}")
                block += f"**Función:** `{name}`\n> {docstring}\n"
            markdown_blocks.append(block)

            smells = detect_smells_python(py_classes, functions)

            resumen_natural = generar_resumen_natural(filename, extension, summary, metricas, smells)
            st.subheader("📝 Resumen en lenguaje natural")
            st.markdown(resumen_natural)
            markdown_blocks.append(f"## 📝 Resumen natural\n{resumen_natural}")

            if smells:
                st.subheader("🚨 Malas prácticas detectadas")
                for issue in smells:
                    st.markdown(f"<div style='color:crimson; font-weight:bold; margin-bottom:8px;'>❗ {issue}</div>", unsafe_allow_html=True)
                if st.button(f"💡 Sugerir mejoras automáticas ({filename})"):
                    sugerencias = sugerencias_mejoras(smells)
                    st.markdown("### ✅ Recomendaciones de mejora:")
                    for sug in sugerencias:
                        st.markdown(f"- {sug}")

                if st.button(f"✨ Generar versión mejorada del código ({filename})"):
                    codigo_mejorado = mejorar_codigo_con_docstrings(code)
                    st.subheader("✨ Código mejorado automáticamente")
                    st.code(codigo_mejorado, language="python")
                    st.download_button("⬇️ Descargar código mejorado", codigo_mejorado, file_name=f"mejorado_{filename}")

        elif extension == "java":
            java_classes = extract_java_elements(code)
            summary = summarize_java_structure(java_classes)
            st.text(summary)
            markdown_blocks.append(f"{summary}")

            st.subheader("📊 Métricas del archivo")
            metricas = obtener_métricas_java(code, java_classes)
            for clave, valor in metricas.items():
                st.markdown(f"**{clave}:** {valor}")
            if st.button(f"📊 Ver gráfico de métricas ({filename})"):
                st.bar_chart(data={k: [v] for k, v in metricas.items()})

            st.subheader("🔍 Clases y métodos detectados (Java)")
            for class_name, methods in java_classes:
                block = f"### Clase: `{class_name}`\n"
                st.markdown(f"### Clase: `{class_name}`")
                for method_name, _ in methods:
                    st.markdown(f"- Método: `{method_name}`")
                    block += f"- Método: `{method_name}`\n"
                markdown_blocks.append(block)

            smells = detect_smells_java(java_classes)

            resumen_natural = generar_resumen_natural(filename, extension, summary, metricas, smells)
            st.subheader("📝 Resumen en lenguaje natural")
            st.markdown(resumen_natural)
            markdown_blocks.append(f"## 📝 Resumen natural\n{resumen_natural}")

            if smells:
                st.subheader("🚨 Malas prácticas detectadas")
                for issue in smells:
                    st.markdown(f"<div style='color:crimson; font-weight:bold; margin-bottom:8px;'>❗ {issue}</div>", unsafe_allow_html=True)
                if st.button(f"💡 Sugerir mejoras automáticas ({filename})"):
                    sugerencias = sugerencias_mejoras(smells)
                    st.markdown("### ✅ Recomendaciones de mejora:")
                    for sug in sugerencias:
                        st.markdown(f"- {sug}")
            else:
                st.markdown("<div style='color:green; font-weight:bold;'>✅ No se han detectado malas prácticas en este archivo.</div>", unsafe_allow_html=True)

        st.subheader("📤 Exportar documentación")
        markdown_text = generar_markdown(filename, summary, markdown_blocks, smells)
        st.download_button("📄 Descargar como Markdown", markdown_text.encode("utf-8"), file_name=f"{filename}.md")
        pdf_file = convertir_pdf(markdown_text)
        st.download_button("📄 Descargar como PDF", pdf_file, file_name=f"{filename}.pdf")

        if "documentos_exportados" not in st.session_state:
            st.session_state["documentos_exportados"] = []
        st.session_state["documentos_exportados"].append((filename, markdown_text, pdf_file))

if st.session_state.get("documentos_exportados"):
    st.divider()
    st.subheader("📦 Descargar toda la documentación como ZIP")

    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, "w") as zipf:
        for fname, md, pdf in st.session_state["documentos_exportados"]:
            zipf.writestr(f"{fname}.md", md)
            zipf.writestr(f"{fname}.pdf", pdf)

    st.download_button(
        "📥 Descargar ZIP completo",
        zip_buffer.getvalue(),
        file_name="documentacion_completa.zip",
        mime="application/zip"
    )
