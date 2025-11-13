Attribute VB_Name = "Módulo1"
Sub GerarExportacao_CSV()
    Dim wsProd As Worksheet, wsTpl As Worksheet
    Dim tbl As ListObject
    Dim i As Long, outRow As Long
    Dim sku As String, nome As String
    Dim preco As Variant, custoTotal As Variant
    Dim exportPath As String, fileName As String, outWB As Workbook
    Dim erros() As Variant, erroLinha As Variant
    Dim resposta As VbMsgBoxResult
    Dim iErro As Long

    Application.ScreenUpdating = False
    On Error GoTo ErrHandler

    Set wsProd = ThisWorkbook.Worksheets("Produtos")
    Set wsTpl = ThisWorkbook.Worksheets("Template para Exportação")

    ' Verifica se há tabela na aba Produtos
    If wsProd.ListObjects.Count = 0 Then
        MsgBox "A aba 'Produtos' não contém nenhuma Tabela. Formate os dados como Tabela primeiro.", vbCritical
        Exit Sub
    End If

    Set tbl = wsProd.ListObjects(1)

    ' Limpa template (a partir da linha 2)
    wsTpl.Range("A2:J10000").ClearContents

    ReDim erros(1 To 1)
    iErro = 0
    outRow = 2

    For i = 1 To tbl.ListRows.Count
        sku = Trim(tbl.DataBodyRange(i, tbl.ListColumns("Código SKU").Index).Value)
        nome = Trim(tbl.DataBodyRange(i, tbl.ListColumns("Nome do Produto").Index).Value)
        preco = tbl.DataBodyRange(i, tbl.ListColumns("Preço de Venda (Clássico)").Index).Value
        custoTotal = tbl.DataBodyRange(i, tbl.ListColumns("Valor do Produto").Index).Value

        ' Validações
        If sku = "" Then
            iErro = iErro + 1
            ReDim Preserve erros(1 To iErro)
            erros(iErro) = Array(i + 1, sku, "SKU vazio", preco, "")
            GoTo NextRow
        End If
        If nome = "" Then
            iErro = iErro + 1
            ReDim Preserve erros(1 To iErro)
            erros(iErro) = Array(i + 1, sku, "Nome vazio", preco, "")
            GoTo NextRow
        End If
        If IsEmpty(preco) Or Not IsNumeric(preco) Then
            iErro = iErro + 1
            ReDim Preserve erros(1 To iErro)
            erros(iErro) = Array(i + 1, sku, "Preço inválido", preco, "")
            GoTo NextRow
        End If
        If IsNumeric(custoTotal) And preco < custoTotal Then
            iErro = iErro + 1
            ReDim Preserve erros(1 To iErro)
            erros(iErro) = Array(i + 1, sku, "Preço < Custo", preco, custoTotal)
            GoTo NextRow
        End If

        ' Mapear para Template (colunas: A:J)
        wsTpl.Range("A" & outRow).Value = sku                      ' IdProduto
        wsTpl.Range("B" & outRow).Value = ""                       ' ID na loja
        wsTpl.Range("C" & outRow).Value = nome                     ' Nome do Produto
        wsTpl.Range("D" & outRow).Value = sku                      ' Código
        wsTpl.Range("E" & outRow).Value = preco                    ' Preço
        wsTpl.Range("F" & outRow).Value = ""                       ' Preço Promocional
        wsTpl.Range("G" & outRow).Value = ""                       ' ID do Fornecedor
        wsTpl.Range("H" & outRow).Value = ""                       ' ID da Marca
        wsTpl.Range("I" & outRow).Value = ""                       ' Link Externo
        wsTpl.Range("J" & outRow).Value = ""                       ' Nome da Loja (Multilojas)

        outRow = outRow + 1
NextRow:
    Next i

    ' Se houver erros, perguntar se deseja criar aba
    If iErro > 0 Then
        resposta = MsgBox("Foram encontrados " & iErro & " erros. Deseja criar uma aba com os detalhes?", vbYesNo + vbExclamation)
        If resposta = vbYes Then
            Dim wsErr As Worksheet
            Set wsErr = ThisWorkbook.Worksheets.Add
            wsErr.Name = "Erros"
            wsErr.Range("A1:E1").Value = Array("LinhaOrigem", "SKU", "Erro", "Valor", "Observação")
            Dim j As Long
            For j = 1 To iErro
                wsErr.Range("A" & j + 1 & ":E" & j + 1).Value = erros(j)
            Next j
        End If
    End If

    ' Salvar Template como CSV na pasta C:\Dados
    exportPath = "C:\Dados"
    fileName = exportPath & "\export_template_" & Format(Now, "yyyymmdd_HHMMSS") & ".csv"
    wsTpl.Copy
    Set outWB = ActiveWorkbook
    Application.DisplayAlerts = False
    outWB.SaveAs fileName:=fileName, FileFormat:=xlCSV, Local:=True
    outWB.Close False
    Application.DisplayAlerts = True

    MsgBox "Exportação concluída: " & fileName, vbInformation

Cleanup:
    Application.ScreenUpdating = True
    Exit Sub
ErrHandler:
    MsgBox "Erro: " & Err.Description, vbCritical
    Resume Cleanup
End Sub

Sub AbrirPastaExportacao()
    Dim pasta As String
    pasta = "C:\Dados"
    Shell "explorer.exe " & pasta, vbNormalFocus
End Sub

Sub LimparExportacao()
    Dim wsTpl As Worksheet
    Set wsTpl = ThisWorkbook.Worksheets("Template para Exportação")
    
    ' Limpa todas as linhas abaixo do cabeçalho (presumido na linha 1)
    wsTpl.Range("A2:J10000").ClearContents
    
    MsgBox "A aba 'Template para Exportação' foi limpa com sucesso.", vbInformation
End Sub
