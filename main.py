import pygame
import os
import random
import neat

ai_jogando = bool
geracao = 0

TELA_LARGURA = 500
TELA_ALTURA = 800

pygame.init()

IMAGE_PIPE = pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'pipe.png')))
IMAGE_FLOOR = pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'base.png')))
IMAGE_BACKGROUND = pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'bg.png')))
IMAGENS_BIRD =[
    pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'bird1.png'))),
    pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'bird2.png'))),
    pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'bird3.png')))
]

pygame.font.init()
FONTE_PONTOS = pygame.font.SysFont('arial', 50)

tela = pygame.display.set_mode((TELA_LARGURA, TELA_ALTURA))
pygame.display.set_icon(IMAGENS_BIRD[0])
pygame.display.set_caption('Flappy Bird')

record = 0

som = pygame.mixer.Sound('sons/coin.mp3')


class Bird:
    IMGS = IMAGENS_BIRD
    ROTACAO_MAX = 25
    VELOCIADADE_ROTACAO = 20
    TIME_DE_ANIMACAO = 5

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.angulo = 0
        self.velocidade = 0
        self.altura = self.y
        self.tempo = 0
        self.contagem_image = 0
        self.image = self.IMGS[0]

    def pular(self):
        self.velocidade = -10.5
        self.tempo = 0
        self.altura = self.y

    def mover(self):
        self.tempo += 1
        deslocamento = 1.5 * (self.tempo**2) + self.velocidade * self.tempo

        if deslocamento > 16:
            deslocamento = 16
        elif deslocamento < 0:
            deslocamento -= 2

        self.y += deslocamento

        if deslocamento < 0 or self.y < (self.altura + 50):
            if self.angulo < self.ROTACAO_MAX:
                self.angulo = self.ROTACAO_MAX
        else:
            if self.angulo > -90:
                self.angulo -= self.VELOCIADADE_ROTACAO

    def desenhar(self, tela):
        self.contagem_image += 1

        if self.contagem_image < self.TIME_DE_ANIMACAO:
            self.image = self.IMGS[0]
        elif self.contagem_image < self.TIME_DE_ANIMACAO * 2:
            self.image = self.IMGS[1]
        elif self.contagem_image < self.TIME_DE_ANIMACAO * 3:
            self.image = self.IMGS[2]
        elif self.contagem_image < self.TIME_DE_ANIMACAO * 4:
            self.image = self.IMGS[1]
        elif self.contagem_image >= self.TIME_DE_ANIMACAO * 4 + 1:
            self.image = self.IMGS[0]
            self.contagem_image = 0

        if self.angulo <= -80:
            self.image = self.IMGS[1]
            self.contagem_image = self.TIME_DE_ANIMACAO * 2

        image_rotacionada = pygame.transform.rotate(self.image, self.angulo)
        pos_centro_image = self.image.get_rect(topleft=(self.x, self.y)).center
        retangulo = image_rotacionada.get_rect(center=pos_centro_image)
        tela.blit(image_rotacionada, retangulo.topleft)

    def get_mask(self):
        return pygame.mask.from_surface(self.image)


class Cano:
    DISTANCE = 200
    SPEED = 5

    def __init__(self, x):
        self.x = x
        self.altura = 0
        self.pos_topo = 0
        self.pos_base = 0
        self.PIPE_TOP = pygame.transform.flip(IMAGE_PIPE, False, True)
        self.PIPE_BASE = IMAGE_PIPE
        self.passou = False
        self.definir_altura()

    def definir_altura(self):
        self.altura = random.randrange(50, 450)
        self.pos_topo = self.altura - self.PIPE_TOP.get_height()
        self.pos_base = self.altura + self.DISTANCE

    def mover(self):
        self.x -= self.SPEED

    def desenhar(self, tela):
        tela.blit(self.PIPE_TOP, (self.x, self.pos_topo))
        tela.blit(self.PIPE_BASE, (self.x, self.pos_base))

    def colidir(self, bird):
        bird_mask = bird.get_mask()
        topo_mask = pygame.mask.from_surface(self.PIPE_TOP)
        base_mask = pygame.mask.from_surface(self.PIPE_BASE)

        distancia_topo = (self.x - bird.x, self.pos_topo  - round(bird.y))
        distancia_base = (self.x - bird.x, self.pos_base - round(bird.y))

        topo_ponto = bird_mask.overlap(topo_mask, distancia_topo)
        base_ponto = bird_mask.overlap(base_mask, distancia_base)

        return True if base_ponto or topo_ponto else False


class Chao:
    SPEED = 5
    LARGURA = IMAGE_FLOOR.get_width()
    IMAGE = IMAGE_FLOOR

    def __init__(self, y):
        self.y = y
        self.x1 = 0
        self.x2 = self.LARGURA

    def mover(self):
        self.x1 -= self.SPEED
        self.x2 -= self.SPEED

        if self.x1 + self.LARGURA < 0:
            self.x1 = self.x2 + self.LARGURA
        if self.x2 + self.LARGURA < 0:
            self.x2 = self.x1 + self.LARGURA

    def desenhar(self, tela):
        tela.blit(self.IMAGE, (self.x1, self.y))
        tela.blit(self.IMAGE, (self.x2, self.y))


def desenhar_tela(tela, birds, pipes, chao, pontos):
    tela.blit(IMAGE_BACKGROUND, (0, 0))
    for bird in birds:
        bird.desenhar(tela)
    for pipe in pipes:
        pipe.desenhar(tela)

    text = FONTE_PONTOS.render(f'Pontuação {pontos}', 0, (255, 255, 255))
    tela.blit(text, (TELA_LARGURA - 10 - text.get_width(), 10))

    if ai_jogando:
        text = FONTE_PONTOS.render(f'Geração {geracao}', 0, (255, 255, 255))
        tela.blit(text, (10, 10))
    else:
        text = FONTE_PONTOS.render(f'Record {record}', 0, (255, 255, 255))
        tela.blit(text, (10, 10))

    chao.desenhar(tela)
    pygame.display.update()


def main(genomas, config):
    global geracao
    global record
    global som
    geracao += 1

    if ai_jogando:
        redes = []
        listas_genomas = []
        birds = []
        for _, genoma in genomas:
            rede = neat.nn.FeedForwardNetwork.create(genoma, config)
            redes.append(rede)

            genoma.fitness = 0
            listas_genomas.append(genoma)

            birds.append(Bird(230, 350))
    else:
        birds = [Bird(230, 350)]
    chao = Chao(730)
    pipes = [Cano(700)]
    pontos = 0
    relogio = pygame.time.Clock()

    rodando = True

    while rodando:
        relogio.tick(30)

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                rodando = False
                pygame.quit()
            if not ai_jogando:
                if evento.type == pygame.KEYDOWN:
                    if evento.key == pygame.K_SPACE:
                        for bird in birds:
                            bird.pular()
            else:
                if evento.type == pygame.KEYDOWN:
                    if evento.key == pygame.K_ESCAPE:
                        menu()

        index_pipe = 0
        if len(birds) > 0:
            if len(pipes) > 1 and birds[0].x > (pipes[0].x + pipes[0].PIPE_TOP.get_width()):
                index_pipe = 1
        else:
            rodando = False
            break

        for i, bird in enumerate(birds):
            bird.mover()
            if ai_jogando:
                listas_genomas[i].fitness += 0.1
                output = redes[i].activate((bird.y, abs(bird.y - pipes[index_pipe].altura),
                                            abs(bird.y - pipes[index_pipe].pos_base)))
                if output[0] > 0.5:
                    bird.pular()

        chao.mover()

        add_pipe = False
        remover_pipes = []
        for pipe in pipes:
            for i, bird in enumerate(birds):
                if pipe.colidir(bird):
                    birds.pop(i)
                    if ai_jogando:
                        listas_genomas[i].fitness -= 1
                        listas_genomas.pop(i)
                        redes.pop(i)
                if not pipe.passou and bird.x > pipe.x:
                    pipe.passou = True
                    add_pipe = True
            pipe.mover()
            if pipe.x + pipe.PIPE_TOP.get_width() < 0:
                remover_pipes.append(pipe)

        if add_pipe:
            pontos += 1
            som.play()
            if ai_jogando:
                for genoma in listas_genomas:
                    genoma.fitness += 5
            else:
                if record < pontos and not ai_jogando:
                    record = pontos
                    with open('vars/record', 'w') as file:
                        file.write(str(record))

            pipes.append(Cano(600))
        for pipe in remover_pipes:
            pipes.remove(pipe)

        for i, bird in enumerate(birds):
            if (bird.y + bird.image.get_height()) > chao.y or bird.y < 0:
                birds.pop(i)
                if ai_jogando:
                    listas_genomas.pop(i)
                    redes.pop(i)

        desenhar_tela(tela, birds, pipes, chao, pontos)


def rodar(caminho_config):
    config = neat.config.Config(neat.DefaultGenome,
                                neat.DefaultReproduction,
                                neat.DefaultSpeciesSet,
                                neat.DefaultStagnation,
                                caminho_config)

    populacao = neat.Population(config)
    populacao.add_reporter(neat.StdOutReporter(True))
    populacao.add_reporter(neat.StatisticsReporter())

    if ai_jogando:
        populacao.run(main, 50)
    else:
        main(None, None)


def menu():
    global ai_jogando
    global record
    global geracao

    geracao = 0

    relogio = pygame.time.Clock()
    relogio.tick(30)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

        tela.blit(IMAGE_BACKGROUND, (0, 0))

        # Exibe o texto do menu
        font = pygame.font.Font(None, 50)
        text1 = font.render('Clique "SPACE" para Jogador', True, (255, 255, 255))
        text2 = font.render('Clique "A" para IA', True, (255, 255, 255))
        tela.blit(text1, (TELA_LARGURA/2 - text1.get_width()/2, TELA_ALTURA/2 - 50))
        tela.blit(text2, (TELA_LARGURA/2 - text2.get_width()/2, TELA_ALTURA/2))

        pygame.display.update()

        teclas = pygame.key.get_pressed()
        if teclas[pygame.K_h] or teclas[pygame.K_SPACE]:
            ai_jogando = False
            with open('vars/record', 'r') as file:
                record = int(file.read())
            caminho_config = 'config.txt'
            rodar(caminho_config)
        elif teclas[pygame.K_a]:
            ai_jogando = True
            caminho_config = 'config.txt'
            rodar(caminho_config)


if __name__ == '__main__':
    menu()
