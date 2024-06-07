<?php

namespace App\Controller;

use App\Entity\Song;
use App\Repository\SongRepository;
use Symfony\Bundle\FrameworkBundle\Controller\AbstractController;
use Symfony\Component\HttpFoundation\Response;
use Symfony\Component\Routing\Attribute\Route;

class GameController extends AbstractController
{
    public function __construct(SongRepository  $songRepository)
    {
        $this->songRepository = $songRepository;

    }

    #[Route('/game', name: 'app_game')]
    public function index(): Response
    {
        $songs = $this->songRepository->findAll();

        return $this->render('game/index.html.twig', [
            'songs' => $songs,
        ]);
    }
}
