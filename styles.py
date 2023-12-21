import io
import os
import httpcore
import gradio as gr
import cv2
from docx import Document
from docx.shared import Pt, Inches
from typing import Any
setattr(httpcore, 'SyncHTTPTransport', Any)
from googletrans import Translator


os.environ["no_proxy"] = "localhost, 127.0.0.1, ::1"
doc = Document('FinalReport_empty.docx')
translator = Translator()


def generate_metadata(file_name, school_name, student_names, field_name, mentor_name, start_date, end_date, title, keywords, header1, text1, image1, text2, header2, text3):
    doc.tables[0].rows[0].cells[2].paragraphs[0].text = school_name
    doc.tables[0].rows[0].cells[4].paragraphs[0].text = student_names
    doc.tables[0].rows[1].cells[2].paragraphs[0].text = field_name
    doc.tables[0].rows[1].cells[4].paragraphs[0].text = mentor_name
    doc.tables[0].rows[2].cells[1].paragraphs[0].text = f"{start_date[0:4]}년 {start_date[4:6]}월 {start_date[6:]}일 ~ {end_date[0:4]}년 {end_date[4:6]}월 {end_date[6:]}일"
    doc.tables[0].rows[3].cells[2].paragraphs[0].text = title
    doc.tables[0].rows[4].cells[2].paragraphs[0].text = translator.translate(title).text
    doc.tables[0].rows[5].cells[1].paragraphs[0].text = keywords

    para = doc.tables[1].rows[0].cells[0].add_paragraph()
    run = para.add_run('I. ' + header1)
    run.bold = True
    run.font.size = Pt(12)
    run.font.name = '맑은 고딕'

    para = doc.tables[1].rows[0].cells[0].add_paragraph()
    run = para.add_run(text1 + '\n')
    run.bold = False
    run.font.size = Pt(10)

    cv2.imwrite("temp.jpg", image1)
    para = doc.tables[1].rows[0].cells[0].add_paragraph()
    run = para.add_run()
    run.add_picture('temp.jpg', height=Inches(3))

    para = doc.tables[1].rows[0].cells[0].add_paragraph()
    para.paragraph_format.left_indent = Pt(10)
    run = para.add_run(text2 + '\n')
    run.bold = False
    run.font.size = Pt(10)


    para = doc.tables[1].rows[0].cells[0].add_paragraph()
    run = para.add_run('II. ' + header2)
    run.bold = True
    run.font.size = Pt(12)
    run.font.name = '맑은 고딕'

    para = doc.tables[1].rows[0].cells[0].add_paragraph()
    run = para.add_run(text3)
    run.bold = False
    run.font.size = Pt(10)
    doc.save(file_name + '.docx')
    print("Done")


with gr.Blocks() as demo:
    file_name = gr.Textbox(label="파일 제목")
    with gr.Column():
        school_name = gr.Textbox(label="학교명")
        student_names = gr.Textbox(label="학번/이름")
    with gr.Column():
        field_name = gr.Textbox(label="분야")
        mentor_name = gr.Textbox(label="멘토명")
    with gr.Column():
        start_date = gr.Textbox(label="시작 날짜 (Ex. YYYYMMDD)")
        end_date = gr.Textbox(label="종료 날짜 (Ex. YYYYMMDD)")
    title = gr.Textbox(label="연구 제목")
    keywords = gr.Textbox(label="키워드 (5개 이상)")
    submit_button = gr.Button(value="Submit")

    files = gr.Files(label='JSON 파일')

    submit_button.click(fn=generate_metadata, inputs=[file_name,
                                                      school_name,
                                                      student_names,
                                                      field_name,
                                                      mentor_name,
                                                      start_date,
                                                      end_date,
                                                      title,
                                                      keywords,
                                                      ])


demo.launch(server_name="0.0.0.0")