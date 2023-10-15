from elevenlabs import set_api_key
set_api_key("36bc6e771f1199dee902338f02f50441")

import argparse
import os
import json
from elevenlabs import Voice, VoiceSettings, generate, play
from docx import Document
import PyPDF2

# Voz padrão
VOZ_PADRAO = "lucas"

def ler_arquivo_docx(caminho):
    doc = Document(caminho)
    texto_completo = []
    for paragrafo in doc.paragraphs:
        texto_completo.append(paragrafo.text)
    return '\n'.join(texto_completo)

def ler_arquivo_pdf(caminho):
    pdf_file = open(caminho, 'rb')
    pdf_reader = PyPDF2.PdfFileReader(pdf_file)
    texto_completo = []
    for page_num in range(pdf_reader.numPages):
        page = pdf_reader.getPage(page_num)
        texto_completo.append(page.extractText())
    pdf_file.close()
    return '\n'.join(texto_completo)

# Carregar detalhes da voz do arquivo JSON
with open('voice_details.json', 'r') as f:
    voice_details = json.load(f)

# Carregar detalhes da voz personalizada do arquivo JSON
with open('custom_voice_details.json', 'r') as f:
    custom_voice_details = json.load(f)

def main():
    parser = argparse.ArgumentParser(description='Converter um arquivo de texto, Word ou PDF em áudio.')
    parser.add_argument('arquivo', type=str, help='Caminho para o arquivo que será convertido em áudio.')
    parser.add_argument('--voz', type=str, default=VOZ_PADRAO, help='Nome da voz a ser usada para a conversão.')
    parser.add_argument('--clone', type=str, default=None, help='Qual voz clonada usar.')
    parser.add_argument('--voice_id', type=str, default=None, help='ID da voz personalizada ou nome amigável.')
    parser.add_argument('--stability', type=float, default=0.71, help='Configuração de estabilidade da voz.')
    parser.add_argument('--similarity_boost', type=float, default=0.5, help='Configuração de similarity_boost da voz.')
    parser.add_argument('--style', type=float, default=0.0, help='Configuração de estilo da voz.')
    parser.add_argument('--use_speaker_boost', type=bool, default=True, help='Usar speaker boost ou não.')
    args = parser.parse_args()

    # Verificar se a voz está disponível
    if not args.clone and not args.voice_id and args.voz not in voice_details:
        print(f"A voz {args.voz} não está disponível. Usando a voz padrão '{VOZ_PADRAO}'.")
        args.voz = VOZ_PADRAO

    extensao = os.path.splitext(args.arquivo)[1]
    if extensao == '.docx':
        texto = ler_arquivo_docx(args.arquivo)
    elif extensao == '.pdf':
        texto = ler_arquivo_pdf(args.arquivo)
    else:
        with open(args.arquivo, 'r', encoding='utf-8') as f:
            texto = f.read()

    if args.voice_id:
        # Buscar o ID de voz real usando o nome amigável
        real_voice_id = custom_voice_details.get(args.voice_id, args.voice_id)

        audio = generate(
            text=texto,
            voice=Voice(
                voice_id=real_voice_id,
                settings=VoiceSettings(
                    stability=args.stability,
                    similarity_boost=args.similarity_boost,
                    style=args.style,
                    use_speaker_boost=args.use_speaker_boost
                )
            )
        )
    elif args.clone:  # Substitua isso pela sua lógica para vozes clonadas
        audio = generate(text=texto, voice=args.clone)
    else:
        audio = generate(
            text=texto,
            voice=args.voz,
            model="eleven_multilingual_v2"
        )

    nome_base = os.path.splitext(args.arquivo)[0]
    nome_audio = f"{nome_base}.wav"

    with open(nome_audio, 'wb') as f:
        f.write(audio)

    play(audio)

if __name__ == '__main__':
    main()
