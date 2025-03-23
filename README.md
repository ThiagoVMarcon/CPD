# Sistema de Gestão Hospitalar

Este é um sistema web para gestão hospitalar que permite o gerenciamento de pacientes, admissões, perguntas/respostas e arquivos médicos.

## Estrutura do Projeto

```
.
├── api/
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── admissions.py
│   │   ├── media.py
│   │   ├── patients.py
│   │   └── questions.py
│   └── services/
│       ├── __init__.py
│       └── blob_storage.py
├── config/
│   └── settings.py
├── static/
│   └── css/
├── templates/
│   └── bdccIndex.html
├── main.py
├── requirements.txt
└── README.md
```

## Funcionalidades

- Gestão de pacientes
- Controle de admissões
- Sistema de perguntas e respostas
- Upload e gerenciamento de arquivos (imagens, vídeos e mensagens)
- Lista de espera em tempo real
- Integração com Google Cloud Platform (BigQuery e Cloud Storage)

## Requisitos

- Python 3.8+
- Google Cloud SDK
- Credenciais do Google Cloud Platform configuradas

## Instalação

1. Clone o repositório
2. Instale as dependências:
```bash
pip install -r requirements.txt
```

3. Configure as credenciais do Google Cloud Platform:
```bash
gcloud auth application-default login
```

4. Execute a aplicação:
```bash
python main.py
```

## Endpoints da API

### Pacientes
- `GET /rest/patients` - Lista todos os pacientes
- `POST /rest/patients` - Cria um novo paciente
- `GET /rest/patient-ids` - Lista IDs dos pacientes
- `GET /rest/services` - Lista serviços disponíveis
- `GET /rest/waiting-list` - Lista de espera atual

### Admissões
- `POST /rest/patients/<patient_id>/admission` - Cria uma nova admissão
- `PUT /rest/patients/<patient_id>/admission/<admission_id>` - Atualiza uma admissão

### Perguntas e Respostas
- `POST /rest/patients/<patient_id>/question` - Cria uma nova pergunta
- `POST /rest/patients/<patient_id>/answer` - Cria uma nova resposta
- `GET /rest/patients/<patient_id>/questions` - Lista perguntas de um paciente
- `GET /rest/questions` - Lista todas as perguntas

### Arquivos
- `POST /rest/patients/<patient_id>/image` - Upload de imagem
- `POST /rest/patients/<patient_id>/video` - Upload de vídeo
- `POST /rest/patients/<patient_id>/message` - Upload de mensagem
- `GET /rest/patients/<patient_id>/files` - Lista arquivos do paciente
- `GET /rest/patients/<patient_id>/messages` - Lista mensagens do paciente
- `POST /rest/setup-folders` - Configura estrutura de pastas

## Contribuição

Para contribuir com o projeto:

1. Fork o repositório
2. Crie uma branch para sua feature (`git checkout -b feature/nova-feature`)
3. Commit suas mudanças (`git commit -am 'Adiciona nova feature'`)
4. Push para a branch (`git push origin feature/nova-feature`)
5. Crie um Pull Request

## Licença

Este projeto está sob a licença MIT. Veja o arquivo LICENSE para mais detalhes.