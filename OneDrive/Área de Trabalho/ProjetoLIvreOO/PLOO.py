import pygame
import random
import sys
import json
LARGURA_TELA = 600
ALTURA_TELA = 660
TAMANHO_TABULEIRO = 10
NUM_MINAS = 15
TAMANHO_CELULA = 60
COR_CABECALHO = (200, 200, 200)
ALTURA_CABECALHO = 60
COR_FUNDO = (100, 200, 200)
COR_LINHA = (50, 50, 50)
COR_CELULA_REVELADA = (200, 200, 200)
COR_TEXTO = (0, 0, 0)
COR_MINA = (255, 0, 0)
COR_BANDEIRA = (255, 255, 0)

ARQUIVO_VITORIAS = "vitorias.json"
pygame.init()
tela = pygame.display.set_mode((LARGURA_TELA, ALTURA_TELA))
pygame.display.set_caption("Campo Minado")
fonte = pygame.font.Font(None, 36)
imagem_mina = pygame.image.load("assets/bomba.png")
imagem_bandeira = pygame.image.load("assets/bandeira.png")
imagem_mina = pygame.transform.scale(
    imagem_mina, (TAMANHO_CELULA, TAMANHO_CELULA))
imagem_bandeira = pygame.transform.scale(
    imagem_bandeira, (TAMANHO_CELULA, TAMANHO_CELULA))


class Celula:
    def __init__(self):
        self.eh_mina = False
        self.revelada = False
        self.marcada = False
        self.minas_adjacentes = 0


class Tabuleiro:
    def __init__(self, tamanho, num_minas):
        self.tamanho = tamanho
        self.num_minas = num_minas
        self.celulas = [[Celula() for _ in range(tamanho)]
                        for _ in range(tamanho)]
        self.posicionar_minas()
        self.c_adjacentes()

    def posicionar_minas(self):
        posicoes = random.sample(
            range(self.tamanho * self.tamanho), self.num_minas)
        for pos in posicoes:
            linha, coluna = divmod(pos, self.tamanho)
            self.celulas[linha][coluna].eh_mina = True

    def c_adjacentes(self):
        direcoes = [(-1, -1), (-1, 0), (-1, 1), (0, -1),
                    (0, 1), (1, -1), (1, 0), (1, 1)]
        for linha in range(self.tamanho):
            for coluna in range(self.tamanho):
                if not self.celulas[linha][coluna].eh_mina:
                    contagem = 0
                    for d_linha, d_coluna in direcoes:
                        l, c = linha + d_linha, coluna + d_coluna
                        if (
                            0 <= l < self.tamanho
                            and 0 <= c < self.tamanho
                            and self.celulas[l][c].eh_mina
                        ):
                            contagem += 1
                    self.celulas[linha][coluna].minas_adjacentes = contagem

    def revelar_celula(self, linha, coluna):
        celula = self.celulas[linha][coluna]
        if celula.revelada or celula.marcada:
            return False
        celula.revelada = True
        if celula.eh_mina:
            return True
        if celula.minas_adjacentes == 0:
            self.revelar_adjacentes(linha, coluna)
        return False

    def revelar_adjacentes(self, linha, coluna):
        direcoes = [(-1, -1), (-1, 0), (-1, 1), (0, -1),
                    (0, 1), (1, -1), (1, 0), (1, 1)]
        for d_linha, d_coluna in direcoes:
            l, c = linha + d_linha, coluna + d_coluna
            if 0 <= l < self.tamanho and 0 <= c < self.tamanho:
                self.revelar_celula(l, c)

    def alternar_bandeira(self, linha, coluna):
        celula = self.celulas[linha][coluna]
        if not celula.revelada:
            celula.marcada = not celula.marcada


def tabuleirot(tabuleiro):
    tela.fill(COR_FUNDO)
    cabecalho(vitorias)
    for linha in range(tabuleiro.tamanho):
        for coluna in range(tabuleiro.tamanho):
            x = coluna * TAMANHO_CELULA
            y = linha * TAMANHO_CELULA + ALTURA_CABECALHO
            celula = tabuleiro.celulas[linha][coluna]
            if celula.revelada:
                if celula.eh_mina:
                    tela.blit(imagem_mina, (x, y))
                elif celula.minas_adjacentes > 0:
                    texto = fonte.render(
                        str(celula.minas_adjacentes), True, COR_TEXTO)
                    tela.blit(texto, (x + TAMANHO_CELULA //
                              3, y + TAMANHO_CELULA // 4))
                else:
                    pygame.draw.rect(tela, COR_CELULA_REVELADA,
                                     (x, y, TAMANHO_CELULA, TAMANHO_CELULA))
            else:
                pygame.draw.rect(
                    tela, COR_FUNDO, (x, y, TAMANHO_CELULA, TAMANHO_CELULA))
                if celula.marcada:
                    tela.blit(imagem_bandeira, (x, y))

            pygame.draw.rect(
                tela, COR_LINHA, (x, y, TAMANHO_CELULA, TAMANHO_CELULA), 2)


def carregar_vitorias():
    try:
        with open(ARQUIVO_VITORIAS, "r") as arquivo:
            dados = json.load(arquivo)
            return dados.get("vitorias", 0)
    except FileNotFoundError:
        salvar_vitorias(0)
        return 0


def salvar_vitorias(vitorias):
    with open(ARQUIVO_VITORIAS, "w") as arquivo:
        json.dump({"vitorias": vitorias}, arquivo, indent=4)


vitorias = carregar_vitorias()


def cabecalho(vitorias):
    pygame.draw.rect(tela, COR_FUNDO, (0, 0, LARGURA_TELA, ALTURA_CABECALHO))
    texto = fonte.render(f"Vitórias : {vitorias}", True, COR_TEXTO)
    tela.blit(texto, (10, 10))


def botao(texto, posicao, largura, altura, cor_fundo, cor_texto):
    fonte_botao = pygame.font.Font(None, 48)
    x, y = posicao
    retangulo = pygame.Rect(x, y, largura, altura)
    pygame.draw.rect(tela, cor_fundo, retangulo)
    pygame.draw.rect(tela, COR_LINHA, retangulo, 2)
    texto_surface = fonte_botao.render(texto, True, cor_texto)
    tela.blit(texto_surface, texto_surface.get_rect(center=retangulo.center))
    return retangulo


def menu(resultado, vitorias):
    tela.fill(COR_FUNDO)
    mensagem = "Você perdeu!" if resultado == "derrota" else "Você venceu!"
    texto_resultado = fonte.render(mensagem, True, COR_MINA)
    texto_vitorias = fonte.render(f"Vitórias : {vitorias}", True, COR_TEXTO)
    tela.blit(texto_resultado, (LARGURA_TELA // 4, ALTURA_TELA // 4))
    tela.blit(texto_vitorias, (LARGURA_TELA // 4, ALTURA_TELA // 4 + 50))
    reiniciar = botao(
        "Reiniciar", (LARGURA_TELA // 3, ALTURA_TELA // 2), 200, 60, (100, 200, 100), COR_TEXTO)
    pygame.display.flip()
    if resultado == "vitoria":
        salvar_vitorias(vitorias)
    esperando = True
    while esperando:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if evento.type == pygame.MOUSEBUTTONDOWN:
                if reiniciar.collidepoint(evento.pos):
                    return


def main():
    global vitorias
    while True:
        tabuleiro = Tabuleiro(TAMANHO_TABULEIRO, NUM_MINAS)
        perdeu = False
        venceu = False
        while not perdeu and not venceu:
            tabuleirot(tabuleiro)
            pygame.display.flip()
            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if evento.type == pygame.MOUSEBUTTONDOWN:
                    x, y = pygame.mouse.get_pos()
                    linha = (y - ALTURA_CABECALHO) // TAMANHO_CELULA
                    coluna = x // TAMANHO_CELULA
                    if linha < 0 or linha >= TAMANHO_TABULEIRO or coluna < 0 or coluna >= TAMANHO_TABULEIRO:
                        continue
                    if evento.button == 1:  # Clique esquerdo
                        perdeu = tabuleiro.revelar_celula(linha, coluna)
                        if perdeu:
                            menu("derrota", vitorias)
                    elif evento.button == 3:  # Clique direito
                        tabuleiro.alternar_bandeira(linha, coluna)
                    if not perdeu and all(
                        celula.revelada or celula.eh_mina
                        for linha in tabuleiro.celulas
                        for celula in linha
                    ):
                        vitorias += 1
                        salvar_vitorias(vitorias)  # Salva a vitória no arquivo
                        venceu = True
                        menu("vitoria", vitorias)
                        break


if __name__ == "__main__":
    vitorias = carregar_vitorias()
    main()
