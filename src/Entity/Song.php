<?php

namespace App\Entity;

use App\Repository\SongRepository;
use Doctrine\DBAL\Types\Types;
use Doctrine\ORM\Mapping as ORM;
use Symfony\UX\Turbo\Attribute\Broadcast;

#[ORM\Entity(repositoryClass: SongRepository::class)]
class Song
{
    #[ORM\Id]
    #[ORM\GeneratedValue]
    #[ORM\Column]
    private ?int $id = null;

    #[ORM\Column(type: Types::TEXT)]
    private ?string $yt_id = null;

    #[ORM\Column(nullable: true)]
    private ?int $timecode = null;

    #[ORM\ManyToOne(inversedBy: 'songs')]
    private ?Movie $movie = null;

    public function getId(): ?int
    {
        return $this->id;
    }

    public function getYtId(): ?string
    {
        return $this->yt_id;
    }

    public function setYtId(string $yt_id): static
    {
        $this->yt_id = $yt_id;

        return $this;
    }

    public function getTimecode(): ?int
    {
        return $this->timecode;
    }

    public function setTimecode(?int $timecode): static
    {
        $this->timecode = $timecode;

        return $this;
    }

    public function getMovie(): ?Movie
    {
        return $this->movie;
    }

    public function setMovie(?Movie $movie): static
    {
        $this->movie = $movie;

        return $this;
    }
}
