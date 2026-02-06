# Game-Python
### **Como o Jogo Funciona:**

#### **Conceito:**
Um jogo chamado **"Fuga do Laboratório"** (Laboratory Escape) onde o jogador controla um personagem de meleca (slime) que deve:
1. Navegar por plataformas
2. Coletar baterias espalhadas pelo cenário
3. Evitar inimigos (aranha, lobo, goblin)
4. Abrir a porta de saída coletando todas as baterias
5. Escapar pelo portal

#### **Componentes Principais:**

**🎮 Player (Personagem)**
- Controle com **Seta Esquerda/Direita** ou **A/D**
- Pulo com **Seta Acima/Espaço**
- Gravidade e física de plataforma
- Duplo pulo (double jump)
- Animações de caminhada, parado e pulo
- Colisão com plataformas

**👹 Inimigos**
- **Aranha** - patrulha em zona
- **Lobo** - se move mais lentamente
- **Goblin** - cobre áreas menores
- Inimigos pausam e revertem direção nas bordas

**🔋 Baterias**
- Itens colecionáveis com animação
- Ao coletar, incrementa contador
- Sons de coleta

**🚪 Porta**
- Inicialmente fechada
- Abre após coletar todas as baterias
- Ao entrar, reinicia o nível

**🎵 Áudio**
- Música de fundo (bg_music.mp3)
- Sons de pulo e coleta
- Toggle de On/Off no menu

#### **Estados do Jogo:**
- **MENU** - Tela inicial com opções
- **PLAY** - Gameplay ativo
- **GAME_OVER** - Tela de morte

---

### **Como Testar o Jogo:**

#### **1️⃣ Pré-requisitos:**
```bash
pip install pygame-zero pygame
```

#### **2️⃣ Preparar Assets:**
Você precisa colocar os arquivos de imagem na pasta `images/`:
- `slime_idle1.png`, `slime_walk1.png`, `slime_walk2.png`, `slime_jump.png`
- `spider1.png`, `spider2.png`, `wolf1.png`, `wolf2.png`, `globin1.png`, `globin2.png`
- `battery1.png`, `battery2.png`
- `door_closed.png`, `door_open.png`
- `tile.png`

E colocar sons na pasta `sounds/`:
- `bg_music.mp3`
- `jump.mp3` (ou criar stub)
- `collect.mp3` (ou criar stub)

#### **3️⃣ Executar o Jogo:**
```bash
python game.py
```

#### **4️⃣ Controles:**
| Ação | Controle |
|------|----------|
| Mover para esquerda | ← ou A |
| Mover para direita | → ou D |
| Pular | ↑ ou ESPAÇO |
| No Menu: Iniciar | Clique em "Start" ou ESPAÇO |
| No Menu: Música | Clique em "Music [On/Off]" |
| No Menu: Sair | Clique em "Exit" |
| Game Over: Voltar | Clique na tela ou ENTER |
