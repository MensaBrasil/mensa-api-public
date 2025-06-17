def download_cert(MB, key) -> str:
    return f"""
        <html>
        <head>
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Download Certificate</title>
            <style>
                body {{
                    font-family: 'Arial', sans-serif;
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    justify-content: center;
                    height: 100vh;
                    margin: 0;
                    background-color: #f2f2f2;
                }}

                .logo {{
                    width: 150px;
                    height: auto;
                    margin-bottom: 20px;
                }}

                .download-btn {{
                    display: inline-block;
                    padding: 10px 20px;
                    font-size: 16px;
                    cursor: pointer;
                    text-align: center;
                    text-decoration: none;
                    outline: none;
                    color: #fff;
                    background-color: #367B48;
                    border: none;
                    border-radius: 15px;
                    box-shadow: 0 9px #6B9E6D;
                    transition: background-color 0.3s, box-shadow 0.3s;
                }}

                .download-btn:hover {{
                    background-color: #2F6140;
                    box-shadow: 0 9px #507C54;
                }}

                .download-btn:active {{
                    background-color: #2F6140;
                    box-shadow: 0 5px #3D5E3D;
                    transform: translateY(4px);
                }}

                .troubleshooting {{
                    margin-top: 15px;
                    font-size: 14px;
                    color: #777;
                    text-align: center;
                    max-width: 300px;
                }}

                .troubleshooting-link {{
                    color: #367B48;
                    text-decoration: none;
                    font-weight: bold;
                }}

                /* Media Queries */
                @media (max-width: 480px) {{
                    .download-btn {{
                        font-size: 14px;
                        padding: 8px 16px;
                    }}
                    
                    .troubleshooting {{
                        font-size: 12px;
                    }}
                }}
            </style>
        </head>
        <body>
            <img src="https://i.imgur.com/9lFJ1bL.png" alt="Logo" class="logo">
            <a href="/download_certificate.png?MB={MB}&key={key}" target="_blank" class="download-btn">Baixar Certificado</a>
            <p class="troubleshooting">Se você enfrentar problemas ao baixar o certificado, você também pode acessá-lo através do <a href="https://carteirinhas.mensa.org.br" class="troubleshooting-link" target="_blank">app versão web</a> em <a href="https://carteirinhas.mensa.org.br" class="troubleshooting-link" target="_blank">carteirinhas.mensa.org.br</a>.</p>
            <div style="margin-top: 15px; font-size: 12px; color: #777; text-align: center; max-width: 300px;">
            <p>
                Seu certificado será baixado como imagem em alta definição. Prefira enviá-lo por email, pois aplicativos como o WhatsApp podem reduzir a qualidade da imagem.
            </p>
        </div>
        </body>
        </html>
        """